"""Cooperatively pause our process group in forecast windows and on pressure."""
import datetime as dt
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

FLOOR = 14 * 1024**3


def disk_reserve():
    # A bounded per-run override never changes the normal 15 GiB reserve.
    gib = float(os.environ.get('STRATA_TYPE_DISK_RESERVE_GIB', '15'))
    if not 14.25 <= gib <= 1024:
        raise ValueError('STRATA_TYPE_DISK_RESERVE_GIB must be at least 14.25')
    return gib * 1024**3

def reason(pressure=True):
    if shutil.disk_usage('/').free < disk_reserve():
        if 'STRATA_TYPE_DISK_RESERVE_GIB' in os.environ:
            raise OSError('Disk below per-run reserve; stopping to preserve the 14 GiB floor')
        return 'disk below configured reserve; preserving 14 GiB floor'
    if Path.home().joinpath('strata-ml/ops/HEAVY_PAUSE').exists():
        return 'shared HEAVY_PAUSE flag'
    sample = subprocess.run(['/usr/sbin/sysctl', '-n', 'kern.memorystatus_vm_pressure_level'], capture_output=True, text=True)
    if pressure and sample.returncode == 0 and int(sample.stdout.strip()) >= 2:
        return 'shared memory pressure'
    if dt.datetime.now(dt.timezone.utc).minute % 15 < 5:
        return 'forecast window'
    return None


def wait_available():
    import gc
    gc.collect()
    start=time.monotonic();previous=None
    while (why := reason()):
        if why != previous:
            print(f'Waiting between units: {why}', flush=True)
            previous=why
        time.sleep(5)
    return time.monotonic()-start


def main():
    args = sys.argv[1:]
    if args and args[0] == '--':
        args.pop(0)
    previous = None
    while (why := reason()):
        if why != previous:
            print(f'Waiting: {why}', flush=True)
            previous = why
        time.sleep(5)
    start = time.monotonic()
    proc = subprocess.Popen(args, start_new_session=True)
    def cancelled(signum, frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, cancelled)
    paused = False
    last = start
    active = 0.0
    try:
        while proc.poll() is None:
            now = time.monotonic()
            if not paused:
                active += now - last
            last = now
            # Memory waits happen at bounded unit boundaries after collection.
            # Suspending mid-unit can retain the allocation causing pressure.
            why = reason(pressure=False)
            if why and not paused:
                os.killpg(proc.pid, signal.SIGSTOP)
                paused = True
                print(f'Paused: {why}', flush=True)
            elif not why and paused:
                os.killpg(proc.pid, signal.SIGCONT)
                paused = False
                print('Resumed', flush=True)
            time.sleep(1)
    except BaseException:
        if paused:
            os.killpg(proc.pid, signal.SIGCONT)
        os.killpg(proc.pid, signal.SIGTERM)
        raise
    if not paused:
        active += time.monotonic() - last
    print(f'Guard: elapsed {time.monotonic()-start:.2f}s, unpaused {active:.2f}s', flush=True)
    raise SystemExit(proc.returncode)

if __name__ == '__main__':
    main()
