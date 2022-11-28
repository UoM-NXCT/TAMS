Runners are containers for multithreading tasks. They extend the functionality of
QThreadPool and QRunnable.

Each script contains a runner. These runners are passed to a threadpool to be run in
parallel. The threadpool is created by some other class, and the runners are passed to
it. The threadpool is then started, and the runners are run in parallel.
