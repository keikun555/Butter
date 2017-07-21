#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "filt.h"

int writecoef(filtername)
char *filtername;
{
 FILE *fd, *fopen();
 char *home, filternamew[256];
 int i, j, k, l, m, n, mm, nn;

/****** Save Filter Coefficients to temp File ********/
 home = getenv("HOME");  /* stdlib.h is necessary to recognize "HOME" */
 sprintf(filternamew, "%s", filtername);
 if ((fd = fopen(filternamew, "w")) == NULL)
   exit( fprintf(stderr, "ERROR[line%d]: fopen in writecoef; file = %s\n", __LINE__, filternamew));

 fprintf(fd, "# ThisFile= %s\n",filternamew);
 fprintf(fd, "FilterFunctions: ");
 if (lowpass00 != 0) fprintf(fd, "Lowpass ");
 if (highpass00 != 0) fprintf(fd, "Highpass ");
 if (notch00 != 0) fprintf(fd, "Notch ");
 if (bandstop00 != 0) fprintf(fd, "Bandstop ");
 fprintf(fd, "\n");
 fprintf(fd, "SamplingFrequency[Hz]= %e\n", smpf);
 if (lowpass00 != 0)
 {
  fprintf(fd, "LowpassFilterCoefficients\n");
  fprintf(fd, "NumberOfPoles= %d x 2\n", lowpass.pole);
  fprintf(fd, "CutoffFrequency[Hz]= %.4f\n", lowpass.cutoff);
  fprintf(fd, "Decay[dB/oct]= %.4f\n", lowpass.decay);
  for (i=0; i<lowpass.pole; i++) fprintf(fd, "%20.16f\n", ggl[i]);
  for (i=0; i<lowpass.pole; i++) fprintf(fd, "%20.16f %20.16f\n", aal[i][0], aal[i][1]);
  for (i=0; i<lowpass.pole;i++) fprintf(fd, "%20.16f %20.16f\n", bbl[i][0], bbl[i][1]);
 }

 if (highpass00 != 0)
 {
  fprintf(fd,"HighpassFilterCoefficients\n");
  fprintf(fd, "NumberOfPoles= %d x 2\n", highpass.pole);
  fprintf(fd, "CutoffFrequency[Hz]= %.4f\n", highpass.cutoff);
  fprintf(fd, "Decay[dB/oct]= %.4f\n", highpass.decay);
  for (i=0; i<highpass.pole; i++) fprintf(fd, "%20.16f\n", ggh[i]);
  for (i=0; i<highpass.pole; i++) fprintf(fd, "%20.16f %20.16f\n", aah[i][0], aah[i][1]);
  for (i=0; i<highpass.pole; i++) fprintf(fd, "%20.16f %20.16f\n", bbh[i][0], bbh[i][1]);
 }

 if (notch00 != 0)
 {
  fprintf(fd, "NotchFilterCoefficients\n");
  fprintf(fd, "NumberOfNotchFilters= %d\n", notch.number);
  for (i=0; i<notch.number; i++)
  {
   fprintf(fd, "NumberOfPoles= %d x 4\n", notch.pole[i]);
   fprintf(fd, "CenterFrequency[Hz]= %.4f\n", notch.freq[i]);
   fprintf(fd, "Decay[dB/oct]= %.4f\n", notch.decay[i]);
   for (j=0; j<notch.pole[i]; j++) fprintf(fd, "%20.16f\n", ggn[i][j]);
   for (j=0; j<notch.pole[i]; j++)
   {
    for (k=0; k<4; k++) fprintf(fd, "%20.16f ", aan[i][j][k]);
    fprintf(fd, "\n");
   }
   for (j=0; j<notch.pole[i]; j++)
   {
    for (k=0; k<4; k++) fprintf(fd, "%20.16f ", bbn[i][j][k]);
    fprintf(fd, "\n");
   }
  }
 }
 if (bandstop00 != 0)
 {
  fprintf(fd, "BandstopFilterCoefficients\n");
  fprintf(fd, "NumberOfPoles= %d x 4\n", bandstop.pole);
  fprintf(fd, "LowCutoffFrequency[Hz]= %.4f\n", bandstop.cutoff1);
  fprintf(fd, "HighCutoffFrequency[Hz]= %.4f\n", bandstop.cutoff2);
  fprintf(fd, "Decay[dB/oct]= %.4f\n", bandstop.decay);
  for (i=0; i<bandstop.pole; i++) fprintf(fd, "%20.16f\n", ggb[i]);
  for (i=0; i<bandstop.pole; i++)
  {
   for (k=0; k<4; k++) fprintf(fd, "%20.16f ", aab[i][k]);
   fprintf(fd, "\n");
  }
  for (i=0; i<bandstop.pole; i++)
  {
   for (k=0; k<4; k++) fprintf(fd, "%20.16f ", bbb[i][k]);
   fprintf(fd, "\n");
  }
 }
 fclose(fd);
 return 1;
}
