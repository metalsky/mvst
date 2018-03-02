/*testcomment*/
#include "Python.h"
#include <fcntl.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>

/*Globals*/
int fp; /*Both functions need access to this but we can't open and close the file within the boundries of any
        /single function, this will be opened once by the module initializer */

/*getLock() will make fnctl calls to do nonblocking or blocking locks depending on the arguements passed*/

static PyObject * lock_getLock(PyObject *self, PyObject *args)
{
  int blockingCall, retVal;
  struct flock myLock;

  if (!PyArg_ParseTuple(args,"i", &blockingCall))
  {
    return NULL; /*NULL indicating arg failure*/
  }

  if(fp < 0)
  {
    perror("Error Opening lock file, check initialization functions");
  /*insert sys.exit(1) python call here*/  
  }

  /*populate mylock*/
  myLock.l_type = F_WRLCK;
  myLock.l_whence = SEEK_SET;
  myLock.l_start = 0;
  myLock.l_len = 0;
  myLock.l_pid = 0;



  if(blockingCall)
  {
    /*It turns out python is incredibly sensitive, in order to make these blocking functions play well*/
    /*With threading in python, we need some happy macros*/
    Py_BEGIN_ALLOW_THREADS /*release global interpreter lock*/
    retVal = fcntl(fp,F_SETLKW,&myLock);
    Py_END_ALLOW_THREADS /*aquire global interpreter lock*/
    return Py_BuildValue("i", retVal);
  }

  else /*non blocking call*/
  {
    retVal = fcntl(fp,F_SETLK,&myLock);
    return Py_BuildValue("i", retVal);
  }

}

/*releaseLock() will release any lock on a file*/
static PyObject * lock_releaseLock(PyObject *self, PyObject *args)
{
  int retVal;
  struct flock myflock;

  if(fp < 0)
  {
    perror("Error with File Pointer, there is a problem in the initialization of this module");
    return Py_BuildValue("i",-1);
  }

 

  myflock.l_type = F_UNLCK;
  myflock.l_whence = SEEK_SET;
  myflock.l_start = 0;
  myflock.l_len = 0;
  myflock.l_pid = 0;

  retVal=fcntl(fp,F_SETLK,&myflock);
  return Py_BuildValue("i", retVal);

}

static PyMethodDef lock_methods[] = 
{
  {"getLock", lock_getLock, METH_VARARGS, "calls fcntl to get a lock on lockfile"},
  {"releaseLock", lock_releaseLock, METH_VARARGS, "releases lock on lockfile"},
  {NULL, NULL}
};


/*Close the file to be neat about things*/
void cleanupModule(void)
{
  close(fp);
}


/*Init function that python needs to load this as a module*/
void initlock() 
{
  fp = open("/home/build/build_scripts/resourceManager/lock", O_RDWR);
  (void) Py_InitModule("lock", lock_methods);
  Py_AtExit((void*)cleanupModule);

}


