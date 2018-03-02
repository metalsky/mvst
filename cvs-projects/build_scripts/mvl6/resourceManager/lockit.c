#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <errno.h>

int main (int argc, char **argv)
{
	int		fd;
	int		ret;
	char		key;
	char		line[200];
	struct flock	myflock;
	char		*filename;

	if (argc < 2) {
		printf("requires an argument\n");
		exit(1);
	}

	filename = argv[1];

	while (1) {
		gets(line);

		key=line[0];

		if (key == '\0') {
			continue;
		}

		if (key == 'o') {
			printf("opening %s\n",filename);

			fd=open(filename, O_RDWR);
			if (fd < 0) {
				perror("error opening");
			} else {
				printf("open returned fd=%d\n",fd);
			}

		} else if (key == 'c') {
			printf("closing %s\n",filename);

			ret=close(fd);
			if (ret < 0) {
				perror("error closing");
			} else {
				printf("close returned %d\n",ret);
			}

		} else if (key == 'b') {
			printf("locking %s (blocking) ...\n",filename);

			myflock.l_type = F_WRLCK;
			myflock.l_whence = SEEK_SET;
			myflock.l_start = 0;
			myflock.l_len = 0;
			myflock.l_pid = 0;

			ret=fcntl(fd,F_SETLKW,&myflock);
			if (ret < 0) {
				perror("error locking with fcntl");
			} else {
				printf("fcntl returned %d\n",ret);
				printf("LOCK ACQUIRED\n");
			}

		} else if (key == 'n') {
			printf("locking %s (non-blocking)\n",filename);

			myflock.l_type = F_WRLCK;
			myflock.l_whence = SEEK_SET;
			myflock.l_start = 0;
			myflock.l_len = 0;
			myflock.l_pid = 0;

			ret=fcntl(fd,F_SETLK,&myflock);
			if (ret < 0) {
				perror("error locking with fcntl");
			} else {
				printf("fcntl returned %d\n",ret);
				printf("LOCK ACQUIRED\n");
			}

		} else if (key == 'u') {
			printf("unlocking %s\n",filename);

			myflock.l_type = F_UNLCK;
			myflock.l_whence = SEEK_SET;
			myflock.l_start = 0;
			myflock.l_len = 0;
			myflock.l_pid = 0;

			ret=fcntl(fd,F_SETLK,&myflock);
			if (ret < 0) {
				perror("error unlocking with fcntl");
			} else {
				printf("fcntl returned %d\n",ret);
				printf("LOCK RELEASED\n");
			}

		} else if (key == 'x') {
			break;
		} else {
			printf("unrecognized key: %c\n",key);
			continue;
		}

		printf("\n");
	}
}
