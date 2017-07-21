#include "filt.h"
#include <float.h>
#include <time.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <ctype.h>
#include <unistd.h>
#include <limits.h>
#include <math.h>

#define MALLOC(x,t) (t *)malloc((x)*sizeof(t))

/* filter/lib/src/ */
extern void createcoef ();
extern int writecoef (char *);
extern int readcoef (char *);
extern int applyfilter (float *, int);

void main(int argc, char **argv)
{
  char filternamer[256], filternamew[256], buf[256];
 int i, j, nsamp;
 float *data01 = NULL;
 FILE fd01, fd02;

 smpf = 3109.0;

 lowpass00 = 1; highpass00 = 1; notch00 = 0; bandstop00 = 0; notch.number = 2;
 sprintf(filternamew, "/home/kimada/filter_c/FilterTemp");
 sprintf(datafile, "/home/kimada/filter_c/wavedata.txt");
 sprintf(outfile, "/home/kimada/filter_c/result.txt");

 createcoef();
 writecoef(filternamew);
 readcoef(filternamew);

 if ((data01 = MALLOC(nsamp, float)) == NULL)
  exit (fprintf(stderr, "\n ##ERROR[line%d]: MALLOC; data01[%d]\n", __LINE__, nsamp));
 else for (i=0; i<nsamp; i++) data01[i] = 0.0;

 /*
 if ((fd01 = fopen(datafile, "r")) == NULL)
  exit(fprintf(stderr, "\n ##ERROR[line%d]: File open failure! [%s]\n", __LINE__, datafile));

 Add a routine that reads the data into data01.
 Example:
 for (i=0; i<nsamp; i++)
 {
  fgets(buf, sizeof(buf), fd01);
  data01[i] = atof(buf);
 }   
 fclose(fd01);
 */

 applyfilter(data01, nsamp);

 /*
 if ((fd02 = fopen(outfile, "w")) == NULL)
  exit(fprintf(stderr, "\n ##ERROR[line%d]: File open failure! [%s]\n", __LINE__, outfile));

 Add a routine that writes the data into a file.
 Example:
 for (i=0; i<nsamp; i++)
  fprintf(fd02, "%f\n", data01[i]);

 fclose(fd02);
 */

}
