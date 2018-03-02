#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdarg.h>
#include <stdint.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>


/*
	VMware header and typedef descriptions
*/

typedef uint64_t SectorType;
typedef uint8_t Bool;

typedef struct SparseExtentHeader {
	uint32_t	magicNumber;
	uint32_t	version;
	uint32_t	flags;
	SectorType	capacity;
	SectorType	grainSize;
	SectorType	descriptorOffset;
	SectorType	descriptorSize;
	uint32_t	numGTEsPerGT;
	SectorType	rgdOffset;
	SectorType	gdOffset;
	SectorType	overHead;
	Bool		uncleanShutdown;
	char		singleEndLineChar;
	char		nonEndLineChar;
	char		doubleEndLineChar1;
	char		doubleEndLineChar2;
	uint8_t		pad[435];
} __attribute__ ((packed)) SparseExtentHeader;

#define SPARSE_MAGICNUMBER 0x564d444b /* 'V' 'M' 'D' 'K' */
#define GRAINSIZE 128
#define NUMGTESPERGT 512

#define DFLTSIZE 2097152

#define SECTOR_SIZE 512
#define PARTMAGIC1 0x55
#define PARTMAGIC2 0xAA

/*
 * Prototypes
 */

static int gen_part(unsigned char *b, int size, char *info);

/*
 * UTILITIES Section
 */

/*volatile*/ void die(char *fmt,...)
{
    va_list ap;

    fflush(stdout);
    fprintf(stderr,"Fatal: ");
    va_start(ap,fmt);
    vfprintf(stderr,fmt,ap);
    va_end(ap);
    fputc('\n',stderr);
    exit(1);
}

static
int resize(int size)
{
int i = 256 * 512;

	while (size > i) i = i *2;
	return(i);
}

static
int do_write(int fd, void *buf, int size)
{
int ret;

	ret = write(fd, buf, size);
	if (ret < 0) die("image write: %s",strerror(errno));
	if (ret != size )
		die("short write: req =%d, actual=%d",size, ret);

	return (ret);
}

static inline
int tst_grain(unsigned char *grain, int size)
{
int i;
	for (i = 0; i < size; i++ )
		if ( grain[i] != 0 ) break;
	return (i == size ? 0 : 1);
}

static
int do_grain_write(int dd, int *gte, int *rgte,
	unsigned char *grain, int lb, int sector, int size)
{
int idx;

	if (tst_grain(grain, size) == 0) return(0);

	idx = lb  / GRAINSIZE;
	gte[idx] = sector;
	rgte[idx] = sector;
	do_write(dd, grain, size);
	return (size/SECTOR_SIZE);	
}

/*************************************************************
 *
 *	Write the main header, and the rest of the file system
 *
 **************************************************************/

main(int argc, char *argv[])
{
int fd, dd;
unsigned char buffer[SECTOR_SIZE], *grains, *ptr;
struct SparseExtentHeader *p;
struct stat filestat;
char srcfile[256] = "STDIN";
char *dstfile, *info;
int gtCoverage, totalGTEs, numGDsects, currentSector, size;
int diskSize;
int n, i, lb, *gtp, *gte, *rgte;

	if (argc < 5) die("Usage %s -o output.vmdk -i infofile [input]\n",
			argv[0]);
	if (argv[1][0] != '-' || argv[1][1] != 'o')
		die("Usage %s -o output.vmdk -i infofile [input]\n",argv[0]);

	dstfile = argv[2];

	if (argv[3][0] != '-' || argv[3][1] != 'i')
		die("Usage %s -o output.vmdk -i infofile [input]\n",argv[0]);

	info = argv[4];

	if (argc < 6) fd = STDIN_FILENO;
	else {
		strncpy(srcfile, argv[5], sizeof(srcfile));
		fd = open(srcfile,O_RDONLY);
	}

	if (fd < 0) die("Unable to open disk image\n");

	if (fstat(fd,&filestat) < 0)
		die("fstat %s: %s",srcfile,strerror(errno));

/* STDIN cannot size the partition so create a default */
	if (fd == STDIN_FILENO ) filestat.st_blocks = DFLTSIZE;

	diskSize = resize(filestat.st_size/SECTOR_SIZE);

	dd = open(dstfile,O_RDWR | O_CREAT | O_TRUNC, 0666);
	if (dd < 0) die("Unable to make vmdk image\n");

	gtCoverage = GRAINSIZE * NUMGTESPERGT;
	totalGTEs = diskSize / gtCoverage;
	numGDsects = 1 + ((totalGTEs * 4) / SECTOR_SIZE);

	p = malloc(sizeof(SparseExtentHeader));
	if ( p == 0 ) die("Malloc header failed");


/* create Sparse header */

	currentSector = 0;
	bzero(p, SECTOR_SIZE);
	p->magicNumber = SPARSE_MAGICNUMBER;
	p->version = 1;
	p->flags = 3;
	p->capacity = diskSize;
	p->grainSize = GRAINSIZE;
	p->descriptorOffset = 1;
	p->descriptorSize = 20;
	p->numGTEsPerGT = NUMGTESPERGT;
	p->rgdOffset = 21;

	p->gdOffset = p->rgdOffset + numGDsects + totalGTEs * 4;
	size = p->gdOffset + numGDsects + totalGTEs *4;
	size += (GRAINSIZE -1);
	size = size/GRAINSIZE;

	p->overHead = size * GRAINSIZE;
	p->uncleanShutdown = 0;
	p->singleEndLineChar = '\n';
	p->nonEndLineChar = ' ';
	p->doubleEndLineChar1 = '\r';
	p->doubleEndLineChar2 = '\n';
	do_write(dd, p, SECTOR_SIZE);
	currentSector++;


/* create Embedded Descriptor */

	bzero(buffer, SECTOR_SIZE);
	ptr = buffer;
	ptr += sprintf(ptr,"# Disk DescriptorFile\n");
	ptr += sprintf(ptr,"version=1\n");
	ptr += sprintf(ptr,"CID=fffffffe\n");
	ptr += sprintf(ptr,"parentCID=ffffffff\n");
	ptr += sprintf(ptr,"createType=\"monolithicSparse\"\n\n");
	ptr += sprintf(ptr,"# Extent description\n");
	ptr += sprintf(ptr,"RW %d SPARSE \"%s\"\n\n",
		diskSize, dstfile);
	ptr += sprintf(ptr,"# The Disk Data Base \n");
	ptr += sprintf(ptr,"#DDB\n\n");
	ptr += sprintf(ptr,"ddb.toolsVersion = \"0\"\n");
	ptr += sprintf(ptr,"ddb.adapterType = \"ide\"\n");
	ptr += sprintf(ptr,"ddb.geometry.sectors = \"63\"\n");
	ptr += sprintf(ptr,"ddb.geometry.heads = \"16\"\n");
	ptr += sprintf(ptr,"ddb.geometry.cylinders = \"%d\"\n",
		diskSize/1008);
	ptr += sprintf(ptr,"ddb.virtualHWVersion = \"3\"\n");
	do_write(dd, buffer, SECTOR_SIZE);
	currentSector++;

	bzero(buffer, SECTOR_SIZE);
	size = p->descriptorSize;
	while ( --size ) {
		do_write(dd, buffer, SECTOR_SIZE);
		currentSector++;
	}

/* create redundant grain table */
	gtp = malloc(numGDsects * SECTOR_SIZE);
	if ( gtp == 0 ) die("Malloc header failed");
	bzero(gtp, numGDsects * SECTOR_SIZE);

	if (currentSector != p->rgdOffset ) die("Sector Miss Count");
	currentSector += numGDsects;

	for (n = 0; n < totalGTEs; n++) {
		gtp[n] = currentSector;
		currentSector += 4;
	}
	do_write(dd, gtp, SECTOR_SIZE * numGDsects);

	size = totalGTEs * 4;

	while ( size-- )
		do_write(dd, buffer, SECTOR_SIZE);

/* create grain table */
	bzero(gtp, numGDsects * SECTOR_SIZE);

	if (currentSector != p->gdOffset ) die("Sector Miss Count");
	currentSector += numGDsects;
	for (n = 0; n < totalGTEs; n++) {
		gtp[n] = currentSector;
		currentSector += 4;
	}
	do_write(dd, gtp, SECTOR_SIZE * numGDsects);

	size = totalGTEs * 4;
	while ( size-- )
		do_write(dd, buffer, SECTOR_SIZE);

/* now allocate the RGTE and GTEs that will go in the reserved space above */

	size = totalGTEs * 4 * 512;
	rgte = malloc(size);
	if ( rgte == 0 ) die("Malloc RGTE failed");
	bzero(rgte, size);

	gte = malloc(size);
	if ( gte == 0 ) die("Malloc GTE failed");
	bzero(gte, size);

/* pad for grain align */
	size = p->overHead - currentSector;
	currentSector += size;
	while ( size-- )
		do_write(dd, buffer, SECTOR_SIZE);


/* Now its time to copy the file */

	grains = malloc(GRAINSIZE * SECTOR_SIZE);
	if ( grains == 0 ) die("Malloc image copy failed");

	bzero(grains, GRAINSIZE * SECTOR_SIZE);

	size = (GRAINSIZE - 63) * SECTOR_SIZE;
	n = read(fd, grains, size);
	if (n != size) die("Short initial read %d, shb %d", n, size);

	ptr = grains;
	if ( ptr[SECTOR_SIZE-2] != PARTMAGIC1 ||
		ptr[SECTOR_SIZE-1] != PARTMAGIC2) {
/* need to create the partition header */
		memmove(&ptr[63 * SECTOR_SIZE], ptr, size);
		bzero(ptr, size);
		gen_part(ptr, diskSize, info);
	} else {
/* fill the rest of the read buffer */
		n = size;
		size = (GRAINSIZE * SECTOR_SIZE) - size;
		n = read(fd, &ptr[n], size);
		if (n != size) die("Bad fill read %d, shb %d", n, size);
	}

/* first Grain is ready to write */
	size = GRAINSIZE * SECTOR_SIZE;
	lb = 0;

	currentSector += do_grain_write(dd, gte, rgte, grains, lb,
				currentSector, size);
	lb += GRAINSIZE;

/* write remaining grains */
	while ((n = read(fd, grains, size)) != 0) {
if (n < size) printf("short read actual = %d, desired = %d\n", n, size);
		currentSector += do_grain_write(dd, gte, rgte, grains,
				lb, currentSector, n);
		lb += n/SECTOR_SIZE;
	}

/* now write back out the Grain Tables */

	size = totalGTEs * 4 * 512;
	lseek(dd, (p->rgdOffset + numGDsects) * SECTOR_SIZE, SEEK_SET);
	do_write(dd, rgte, size);
	lseek(dd, (p->gdOffset + numGDsects) * SECTOR_SIZE, SEEK_SET);
	do_write(dd, gte, size);

	if(close(dd) != 0) die("vmdk close failed %s",strerror(errno));
	if(close(fd) != 0) die("raw image close failed %s",strerror(errno));

	exit(0);
}

/*
 * Partition header
 */

struct partition {
	unsigned char boot_ind;         /* 0x80 - active */
	unsigned char head;             /* starting head */
	unsigned char sector;           /* starting sector */
	unsigned char cyl;              /* starting cylinder */
	unsigned char sys_ind;          /* What partition type */
	unsigned char end_head;         /* end head */
	unsigned char end_sector;       /* end sector */
	unsigned char end_cyl;          /* end cylinder */
	unsigned int start4;        /* starting sector counting from 0 */
	unsigned int size4;         /* nr of sectors in partition */
} __attribute__ ((packed));

#define pt_offset(b,n) ((struct partition *)((b) + 0x1be + \
				(n) * sizeof(struct partition)))
unsigned char mbr[] = {
0xfa, 0xeb, 0x21, 0x01, 0xb5, 0x01, 0x4c, 0x49,
0x4c, 0x4f, 0x16, 0x06, 0x0c, 0x40, 0x62, 0x45,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0xf6, 0x9a, 0x60, 0x69, 0x01, 0x00, 0x80, 0x60,
0x27, 0xb7, 0x07, 0x00, 0xb8, 0xc0, 0x07, 0x8e,
0xd0, 0xbc, 0x00, 0x08, 0xfb, 0x52, 0x53, 0x06,
0x56, 0xfc, 0x8e, 0xd8, 0x31, 0xed, 0x60, 0xb8,
0x00, 0x12, 0xb3, 0x36, 0xcd, 0x10, 0x61, 0xb0,
0x0d, 0xe8, 0x67, 0x01, 0xb0, 0x0a, 0xe8, 0x62,
0x01, 0xb0, 0x4c, 0xe8, 0x5d, 0x01, 0x60, 0x1e,
0x07, 0x80, 0xfa, 0xfe, 0x75, 0x02, 0x88, 0xf2,
0xbb, 0x00, 0x02, 0x8a, 0x76, 0x1e, 0x89, 0xd0,
0x80, 0xe4, 0x80, 0x30, 0xe0, 0x78, 0x0a, 0x3c,
0x10, 0x73, 0x06, 0xf6, 0x46, 0x1c, 0x40, 0x75,
0x2e, 0x88, 0xf2, 0x66, 0x8b, 0x76, 0x18, 0x66,
0x09, 0xf6, 0x74, 0x23, 0x52, 0xb4, 0x08, 0xb2,
0x80, 0x53, 0xcd, 0x13, 0x5b, 0x72, 0x55, 0x0f,
0xb6, 0xca, 0xba, 0x7f, 0x00, 0x42, 0x66, 0x31,
0xc0, 0x40, 0xe8, 0x70, 0x00, 0x66, 0x3b, 0xb7,
0xb8, 0x01, 0x74, 0x03, 0xe2, 0xef, 0x5a, 0x53,
0x8a, 0x76, 0x1f, 0xbe, 0x20, 0x00, 0xe8, 0x4a,
0x00, 0xb4, 0x99, 0x66, 0x81, 0x7f, 0xfc, 0x4c,
0x49, 0x4c, 0x4f, 0x75, 0x27, 0x5e, 0x68, 0x80,
0x08, 0x07, 0x31, 0xdb, 0xe8, 0x34, 0x00, 0x75,
0xfb, 0xbe, 0x06, 0x00, 0x89, 0xf7, 0xb9, 0x0a,
0x00, 0xf3, 0xa6, 0x75, 0x0d, 0xb0, 0x02, 0xae,
0x75, 0x08, 0x06, 0x55, 0xb0, 0x49, 0xe8, 0xd2,
0x00, 0xcb, 0xb4, 0x9a, 0xb0, 0x20, 0xe8, 0xca,
0x00, 0xe8, 0xb7, 0x00, 0xfe, 0x4e, 0x00, 0x74,
0x07, 0xbc, 0xe8, 0x07, 0x61, 0xe9, 0x5e, 0xff,
0xf4, 0xeb, 0xfd, 0x66, 0xad, 0x66, 0x09, 0xc0,
0x74, 0x0a, 0x66, 0x03, 0x46, 0x10, 0xe8, 0x04,
0x00, 0x80, 0xc7, 0x02, 0xc3, 0x60, 0x55, 0x55,
0x66, 0x50, 0x06, 0x53, 0x6a, 0x01, 0x6a, 0x10,
0x89, 0xe6, 0x53, 0xf6, 0xc6, 0x60, 0x74, 0x58,
0xf6, 0xc6, 0x20, 0x74, 0x14, 0xbb, 0xaa, 0x55,
0xb4, 0x41, 0xcd, 0x13, 0x72, 0x0b, 0x81, 0xfb,
0x55, 0xaa, 0x75, 0x05, 0xf6, 0xc1, 0x01, 0x75,
0x4a, 0x52, 0x06, 0xb4, 0x08, 0xcd, 0x13, 0x07,
0x72, 0x59, 0x51, 0xc0, 0xe9, 0x06, 0x86, 0xe9,
0x89, 0xcf, 0x59, 0xc1, 0xea, 0x08, 0x92, 0x40,
0x83, 0xe1, 0x3f, 0xf7, 0xe1, 0x93, 0x8b, 0x44,
0x08, 0x8b, 0x54, 0x0a, 0x39, 0xda, 0x73, 0x39,
0xf7, 0xf3, 0x39, 0xf8, 0x77, 0x33, 0xc0, 0xe4,
0x06, 0x86, 0xe0, 0x92, 0xf6, 0xf1, 0x08, 0xe2,
0x89, 0xd1, 0x41, 0x5a, 0x88, 0xc6, 0xeb, 0x06,
0x66, 0x50, 0x59, 0x58, 0x88, 0xe6, 0xb8, 0x01,
0x02, 0xeb, 0x02, 0xb4, 0x42, 0x5b, 0xbd, 0x05,
0x00, 0x60, 0xcd, 0x13, 0x73, 0x10, 0x4d, 0x74,
0x0a, 0x31, 0xc0, 0xcd, 0x13, 0x61, 0x4d, 0xeb,
0xf0, 0xb4, 0x40, 0xe9, 0x46, 0xff, 0x8d, 0x64,
0x10, 0x61, 0xc3, 0xc1, 0xc0, 0x04, 0xe8, 0x03,
0x00, 0xc1, 0xc0, 0x04, 0x24, 0x0f, 0x27, 0x04,
0xf0, 0x14, 0x40, 0x60, 0xbb, 0x07, 0x00, 0xb4,
0x0e, 0xcd, 0x10, 0x61, 0xc3, 0x00, 0x00, 0x00,
0xf6, 0x9a, 0x60, 0x69, 0xcf, 0xc9
};

#define MAP_OFF 12
#define TS_OFF 20
#define SER_OFF 24
#define SEC_OFF 32

int
gen_part(unsigned char *buf, int size, char *infofile) {
struct partition *b;
int i;
int fd;

	memcpy(buf, mbr, sizeof(mbr));
	fd = open(infofile, O_RDONLY);
	if(fd < 0) die("boot info missing: %s", strerror(errno));
	read(fd, &buf[MAP_OFF], 4);
	read(fd, &buf[SER_OFF], 4);
	read(fd, &buf[SEC_OFF], 4);
	memcpy(&buf[TS_OFF], &buf[MAP_OFF], 4);
	close(fd);
	
	b = pt_offset(buf, 0);
	b->boot_ind  = 0;
	b->head      = 1; /* head idx starts at 1 */
	b->sector    = 1; /* sector idx starts at 1 */
	b->cyl       = 0; /* cyl starts at 0 */
	b->sys_ind   = 0x83; 
	b->end_head  = 0xf;
	b->end_sector= 0xff;
	b->end_cyl   = 0xff;
	b->start4    = 63;
	b->size4     = (size / 1008) * 1008 - 63;
	buf[SECTOR_SIZE-2] = PARTMAGIC1;
	buf[SECTOR_SIZE-1] = PARTMAGIC2;
}
