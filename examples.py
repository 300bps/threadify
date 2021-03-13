# Examples demonstrating the usage of Threadify.
#
# David Smith
# 3/12/21

import time
from threadify import Threadify
import queue



def task_dots(storage):
    """
    Task that prints dots forever.
    """
    print(".", sep=" ", end="", flush=True)
    time.sleep(.25)
    return True


def task_symbols(storage):
    """
    Task that prints first character of contents of storage["symbol"] forever.
    """
    sym = storage.get("symbol", ".")
    print(sym[0], sep=" ", end="", flush=True)
    time.sleep(.25)
    return True


def task_storage(storage):
    """
    Demonstrates a periodic task accessing and modifying storage.
    """
    # Values in storage persist from call to call. Local variables do not

    # In case storage values haven't been passed in, set defaults
    storage.setdefault("a", 1)
    storage.setdefault("b", "A")

    # Do work
    print(storage)

    # Operate on storage
    storage["a"] += 1

    # Fetch from storage, operate
    tmp = storage["b"]
    tmp = chr((ord(tmp) - ord("A") + 1) % 26 + ord("A"))

    # Update storage
    # Note: for value to persist, it must be assigned back to storage
    storage["b"] = tmp

    # Sleep allows other threads to run
    time.sleep(1)

    return True



def task_run_5s(storage):
    """
    Demonstrates self-terminating task.
    Use storage to pass in a start time so that task can decide when to self-terminate.
    """
    # Get start time from storage
    start = storage.get("start_time")

    # Compute elapsed time and print
    delta = time.time() - start
    print("Elapsed time: {:4.2f}".format(delta))

    # Time to die?
    if delta >= 5:
        print("Stopping after {:4.2f} seconds".format(delta))

        # Signal thread to terminate
        return False

    # Sleep allows other threads to run
    time.sleep(0.5)

    # Signal thread to keep running
    return True


def exception_task(storage):
    # Get start time from storage
    start = storage.get("start_time")

    # Compute elapsed time and print
    delta = time.time() - start
    print("Elapsed time: {:4.2f}".format(delta))

    # Sleep allows other threads to run
    time.sleep(1)

    # Time to kill?
    if delta >= 5:
        print("Raising exception after {:4.2f} seconds".format(delta))

        # Signal thread to terminate
        raise Exception("Exception thrown from task!")

    # Signal thread to keep running
    return True


def task_checkqueue(storage):
    """
    Task that watches a queue for messages and acts on them when received.
    """
    # Get the queue object from the storage dictionary
    thequeue = storage.get("queue")
    try:
        # Use a timeout so it blocks for at-most 0.5 seconds while waiting for a message. Smaller values can be used to
        # increase the cycling of the task and responsiveness to Threadify control signals (like pause) if desired.
        msg = thequeue.get(block=True, timeout=.5)
    except queue.Empty:
        print("_", end="")
    else:
        if msg == "QUIT":
            return False

        # Print received message
        print("{:s}".format(msg), end="")

    return True

def task_dosomething(storage):
    """
    Task that gets launched to handle something in the background until it is completed and then terminates. Note that
    this task doesn't return until it is finished, so it won't be listening for Threadify pause or kill requests.
    """
    # An important task that we want to run in the background.
    for i in range(10):
        print(i, end="")
        time.sleep(1)

    return False


# Sequentially run through a series of examples
if __name__ == "__main__":
    # Enable debug outputs
    Threadify.ENABLE_DEBUG_OUTPUT = True


    # ** EXAMPLE 1) Simplest example - built-in task displays '.' to the screen each 0.25 seconds. **
    print("\nEX 1) Print '.' approximately every 0.25 seconds.")

    t1 = Threadify(start=True)
    # Main program sleeps here while task continues to run
    time.sleep(5)

    # Send kill request and wait for it to complete
    t1.kill(wait_until_dead=True)
    print("Done")


    # ** EXAMPLE 2) Demonstrate two tasks running with one being paused and later continued. **
    print("\nEX 2) Starting 2 tasks - one will be paused and later continued while the first runs continuously.")

    # Pass initial value of "symbol" via the storage dictionary to each task
    t1 = Threadify(task_symbols, {"symbol": "X"})
    t2 = Threadify(task_symbols, {"symbol": "O"})

    # Start tasks manually (could also have been automatically started by using the start parameter)
    t1.start()
    t2.start()

    time.sleep(5.1)
    print("\nPausing 'X' for 5 seconds.")
    t1.pause(True)
    time.sleep(5)

    print("\nUnpausing 'X' for 5 seconds.")
    t1.unpause()
    time.sleep(5)

    t1.kill()
    t2.kill()
    t1.join()
    t2.join()
    print("Done")


    # ** EXAMPLE 3) Demonstrate a task that self-terminates after 5 seconds. **
    print("\nEX 3) Demonstrate a task that self-terminates after 5 seconds.")

    t1 = Threadify(task_run_5s, {"start_time": time.time()}, daemon=False, start=True)

    # Join instructs main program to wait on t1 to complete before continuing
    t1.join()
    print("Done")


    # ** EXAMPLE 4) Demonstrate communication with a task via a queue passed in through storage. **
    print("\nEX 4) Demonstrate communication with a task via a queue passed in through storage.")

    # Create a thread-safe queue for message passing
    q = queue.Queue()

    # This instance REQUIRES deep_copy=FALSE since Queue is not pickleable.
    t1 = Threadify(task_checkqueue, {"queue": q}, deep_copy=False, start=True)
    # Wait 3 seconds - then send some messages with varying delays interspersed
    time.sleep(3)
    q.put("HE")
    q.put("LLO")
    q.put(" WORLD")
    time.sleep(2)
    q.put("1")
    time.sleep(1)
    q.put("2")
    time.sleep(2)
    q.put("3")
    time.sleep(3)

    # Send the QUIT message to have task kill itself and then wait for it to die
    q.put("QUIT")
    t1.join()
    print("Done.")


    # ** EXAMPLE 5) Fire and forget. Launch a function in a separate thread and have it run to completion. **
    print("\nEX 5) Fire and forget. Launch a function in a separate thread and have it run to completion.")

    t1 = Threadify(task_dosomething, start=True)

    # Join instructs main program to wait on t1 to complete before continuing
    t1.join()
    print("Done")


    # Additional examples to be explored
    """
    # ## EXAMPLE) Example of a periodic task accessing and modifying persistent storage ##
    print("\nExample of a periodic task accessing and modifying persistent storage.")
    
    t1 = Threadify(task_storage, storage={"a": 10, "b": "A"}, start=True)
    time.sleep(10)
    t1.kill(wait_until_dead=True)
    print("Done")
    
    
    # ## Exceptions thrown from task body and not ignored ##
    t1 = Threadify(exception_task, {"start_time": time.time()}, ignore_task_exceptions=False)
    t1.daemon = False
    t1.start()
    print("\nTask raises exceptions after 5 seconds and doesn't dispose.")
    time.sleep(8)
    t1.kill()
    t1.join()
    print("Done")


    # ## Exceptions thrown from task body and ignored ##
    t1 = Threadify(exception_task, {"start_time": time.time()}, ignore_task_exceptions=True)
    t1.daemon = False
    t1.start()
    print("\nTask raises exceptions after 5 seconds; disposes of them an continues for 3 more seconds.")
    time.sleep(8)
    t1.kill()
    t1.join()
    print("Done")


    # ## kill a paused thread ##
    t1 = Threadify(task_dots, {"a": 123, "b": "M"}, daemon=False)
    t1.start()
    print("\nStarting a thread that will be paused and then killed.")
    time.sleep(5)
    t1.pause(True)    
    print("\nPaused for 5 seconds.")
    time.sleep(5)
    
    print("kill paused thread.")
    t1.kill()
    t1.join()
    print("Done")
    """
