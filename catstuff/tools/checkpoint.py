"""
This package requires two pieces of 'hacky' code and should not be used in production outside this application
"""

import inspect, ctypes
import shelve, dbm
import tempfile, os, sys
import functools

'''
Requires that the variables in the parent namespace be manipulated
'''
class ParentNamespace:
    """ Provides a set of methods to manipulate the namespace of the parent scope"""
    def __init__(self, depth: int=1):
        self.depth = depth

        static_methods = {'locals', 'set', 'delete'}
        for method in static_methods:
            setattr(self, method, functools.partial(getattr(self, method), depth=depth))

    def __getitem__(self, item):
        try:
            return self.locals(depth=self.depth+1)[item]
        except KeyError as e:
            raise NameError('{} is not defined'.format(item)) from e

    def __setitem__(self, key, value):
        self.set(key, value, depth=self.depth+1)  # depth must compensate for this function

    def __delitem__(self, key):
        self.delete(key, depth=self.depth+1)

    @staticmethod
    def locals(depth=1) -> dict:
        """
        Return the locals of a parent namespace
        :param depth: Depth of parent where 0 represents the current namespace
        :type: positive int (default=1)
        :return:
        """
        frame = inspect.currentframe()
        try:
            f = frame.f_back
            for d in range(depth):
                f = f.f_back
            return f.f_locals
        finally:
            del frame

    @staticmethod
    def set(var, value, depth: int=1):
        """
        Sets a variable in the parent namespace
        :var: name of variable
        :type: str
        :param: value: value of variable
        :param depth: Depth of parent where 0 represents the current namespace
        :type: positive int (default=1)
        :return:
        """

        # This function is a hack to emulate the nonlocal keyword dynamically
        # Originally, this hack was designed for python2 but the dynamic property
        # still makes it useful in python3
        locals_to_fast = ctypes.pythonapi.PyFrame_LocalsToFast
        locals_to_fast.restype = None
        locals_to_fast.argtypes = [ctypes.py_object, ctypes.c_int]

        frame = inspect.currentframe()
        try:
            f = frame.f_back
            for d in range(depth):
                f = f.f_back
            f.f_locals[var] = value
            locals_to_fast(f, 1)  # a hack to emulate nonlocal keyword dynamically
        finally:
            del frame

    @staticmethod
    def delete(var, depth: int=1):
        """
        Deletes a variable in the parent namespace
        :param depth: Depth of parent where 0 represents the current namespace
        :type: positive int (default=1)
        :return:
        """
        locals_to_fast = ctypes.pythonapi.PyFrame_LocalsToFast
        locals_to_fast.restype = None
        locals_to_fast.argtypes = [ctypes.py_object, ctypes.c_int]

        frame = inspect.currentframe()
        try:
            f = frame.f_back
            for d in range(depth):
                f = f.f_back
            del f.f_locals[var]
            locals_to_fast(f, 1)  # hack to emulate nonlocal keyword dynamically
        finally:
            del frame


class _SkipWith(Exception):
    pass


class Checkpoint:
    """
    Context manager for creating checkpoints
    """
    '''
    Requires that the with-block can be skipped
    
    """ https://code.google.com/archive/p/ouspg/wikis/AnonymousBlocksInPython.wiki"""
    '''
    def __init__(self, path=None, locals: dict=None, cache_time=86400):
        self.locals = locals

        self.cache_time = cache_time  # in seconds

        if path is None:
            """ 
            Generate a filename based on the call stack
            There may be collisions but I will assume they are super rare
            We are extracting simple metadata from each frame in the stack that
            make each call unique (namely the filename and lineno) 
            """

            from hashlib import sha512
            import __main__

            h = sha512()
            stack = inspect.stack()

            # It is necessary to determine the start/end indices of the stack
            # in case you are running a debugger -- the debugger creates additional
            # frames in the stack
            stack_start = None
            stack_end = None
            for i, frame in enumerate(stack):
                if stack_start is None:
                    if frame.filename == __file__:
                        stack_start = i
                else:
                    if frame.filename == __main__.__file__:
                        stack_end = i

            for frame in stack[stack_start:stack_end]:
                for field in ['filename', 'function', 'index', 'lineno']:
                    h.update(str(getattr(frame, field)).encode())

            tmp = tempfile.gettempdir()
            file = h.hexdigest()
            self.path = os.path.join(tmp, file)
        else:
            self.path = path

    @property
    def realpath(self):
        with shelve.open(self.path, 'c') as db:  # mode should either be 'c' or 'r'
            return db.dict._datfile

    def __call__(self, func, *args, **kwargs):
        """ Checkpoint decorator"""
        '''
        The problem with this implementation is that variables assigned within
        the function have no way of making it to the outer score automatically
        
        There are two workarounds that can be implemented by the developer
        
        1. Use 'nonlocal' keyword. This requires that the variable is initialized
        in the same scope as the checkpoint
        
        foo = None  # init foo
        @Checkpoint()
        def func():
            nonlocal foo
            foo = 'bar'
        
        func()  # foo will be checkpointed with a value of 'bar' after execution
   
        2. Use the ParentNamespace class to inject the namespace of the function to the parent
        
        @Checkpoint()
        def func():
            foo = 'bar'
            
            for var, value in locals().items():
                ParentNamespace(depth=2).set(var, value)  # depth increases due to decorator
        
        func()  # foo will be checkpointed with a value of 'bar' after execution
        
        '''
        def wrapper():
            if self.isvalid():
                self.load(depth=1)
            else:
                func()
            self.save(depth=1)
        return wrapper

    def __enter__(self):
        if self.isvalid():
            self.load(depth=1)
            # with-hacks magic -- skip with-block
            # self._skip_block()

            # _skipblock not working atm, for the moment, do the skipping manually
            # with Checkpoint() as cp:
            #    if cp.isvalid:
            #        raise _SkipWith
        return self

    def skip_with(self):
        """ Temporary workaround"""
        if self.isvalid():
            raise _SkipWith

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type in {None, _SkipWith}:  # with-block completed without exception
            # We want to save the namespace if the block completed successfully
            # or the block was skipped (since we are checking mtimes)
            self.save(depth=1)
            return True

    def _skip_block(self):
        """ Withhacks..."""

        raise NotImplementedError('The with-hack is not working atm')

        # Enable tracing by setting the globals tracing func to
        # anything true-ish. Otherwise setting the calling frame's
        # tracing function does nothing.
        sys.settrace(lambda *args, **keys: None)

        # Capture the calling frame, its current instruction pointer
        # value and set the magical tracing function.
        frame = inspect.currentframe()
        frame.f_trace = self._trace

    def _trace(self, frame, event, arg):
        raise _SkipWith

    def isvalid(self) -> bool:
        """ Return True if the db is valid"""
        if self._check_exist():
            checks = [self._check_mtime]
            for check in checks:
                if check() is False:
                    return False
            return True
        return False

    def _check_exist(self) -> bool:
        """ Return True if file already exists"""
        try:
            shelve.open(self.path, 'r')
            return True
        except dbm.error:
            return False

    def _check_mtime(self):
        """ Return True if within cache time"""
        from time import time
        mtime = os.stat(self.realpath).st_mtime
        return True if time() - mtime < self.cache_time else False

    def save(self, depth: int=0) -> str:
        """
        Saves the checkpoint to disk and returns the path to file
        :param depth: Depth of namespace where 0 is the namespace called from
        :type positive int=0
        :return: checkpoint path
        :rtype: str
        """
        locals = self.locals
        if locals is None:
            locals = ParentNamespace(depth=depth+1).locals()
        with shelve.open(self.path, 'n') as db:
            for var, value in locals.items():
                try:
                    db[var] = value
                except (TypeError, AttributeError):
                    pass
            return self.realpath

    def load(self, depth: int=0) -> bool:
        """
        Return True if values were loaded successfully
        :param depth: Depth of namespace where 0 is the namespace called from
        :type positive int=0
        :return:
        :rtype: bool
        """

        with shelve.open(self.path, 'r') as db:
            parent = ParentNamespace(depth=depth+1)
            for var, value in db.items():
                try:
                    parent.set(var, value)
                except Exception:
                    # TODO: logging
                    return False
            return True

