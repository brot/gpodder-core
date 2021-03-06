#
# gpodder.log - Logging setup (2013-03-02)
# Copyright (c) 2012, 2013, Thomas Perl <m@thp.io>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
#


import gpodder

import glob
import logging
import os
import sys
import time
import traceback

logger = logging.getLogger(__name__)

def setup(home=None, verbose=True):
    # Configure basic stdout logging
    STDOUT_FMT = '%(created)f [%(name)s] %(levelname)s: %(message)s'
    logging.basicConfig(format=STDOUT_FMT,
            level=logging.DEBUG if verbose else logging.WARNING)

    # Replace except hook with a custom one that logs it as an error
    original_excepthook = sys.excepthook
    def on_uncaught_exception(exctype, value, tb):
        message = ''.join(traceback.format_exception(exctype, value, tb))
        logger.error('Uncaught exception: %s', message)
        original_excepthook(exctype, value, tb)
    sys.excepthook = on_uncaught_exception

    if home and os.environ.get('GPODDER_WRITE_LOGS', 'yes') != 'no':
        # Configure file based logging
        logging_basename = time.strftime('%Y-%m-%d.log')
        logging_directory = os.path.join(home, 'Logs')
        if not os.path.isdir(logging_directory):
            try:
                os.makedirs(logging_directory)
            except:
                logger.warn('Cannot create output directory: %s',
                        logging_directory)
                return False

        # Keep logs around for 5 days
        LOG_KEEP_DAYS = 5

        # Purge old logfiles if they are older than LOG_KEEP_DAYS days
        old_logfiles = glob.glob(os.path.join(logging_directory, '*-*-*.log'))
        for old_logfile in old_logfiles:
            st = os.stat(old_logfile)
            if time.time() - st.st_mtime > 60*60*24*LOG_KEEP_DAYS:
                logger.info('Purging old logfile: %s', old_logfile)
                try:
                    os.remove(old_logfile)
                except:
                    logger.warn('Cannot purge logfile: %s', exc_info=True)

        root = logging.getLogger()
        logfile = os.path.join(logging_directory, logging_basename)
        file_handler = logging.FileHandler(logfile, 'a', 'utf-8')
        FILE_FMT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
        file_handler.setFormatter(logging.Formatter(FILE_FMT))
        root.addHandler(file_handler)

    logger.debug('==== gPodder starts up ====')

    return True

