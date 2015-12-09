import scrapy.cmdline as cmdline
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start spider process(es).')
    parser.add_argument('--job_dir','-s', type=str, help='job directory if execution should save its state to be resumable')
    parser.add_argument('--output_filename','-o', type=str, help='filename for export')
    parser.add_argument('--output_filetype','-t', type=str, help='file type for export')
    parser.add_argument('--log_level', '-L', type=str, help='log level')

    parser.add_argument('spider', metavar='-c', type=str, help='name of the spider to run')
    # cmdline.execute('scrapy crawl authorLabels -s JOBDIR=crawls/author_labels -o popular_names.csv -t csv'.split(' '))
    args = parser.parse_args()

    command = 'scrapy crawl %s' % args.spider
    if args.job_dir:
        command += ' -s JOB_DIR=%s' % args.job_dir
    if args.output_filename:
        command += ' -t %s' % args.output_filename
    if args.output_filetype:
        command += ' -o %s' % args.output_filetype
    if args.log_level:
        command += ' -L %s' % args.log_level
    cmdline.execute(command.split(' '))
