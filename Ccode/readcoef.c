#include <filt.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

extern int strdecomp (char *, char *);

int readcoef(filtername)
char *filtername;
{
 FILE *fd;
 char *home, filternamer[256];
 char linebuf[2048], buf[100], buf1[4][100], bufa[100], buffer[100];
 int er, coefline, poleA;
 int i, j, k, l, m, n, mm, nn;

 sprintf(filternamer, "%s", filtername);
 if ((fd = fopen(filternamer, "r")) == NULL)
   exit( fprintf(stderr, "ERROR[line%d]: fopen in readcoef; file = %s\n", __LINE__, filternamer));
 coefline = 0;
 while (1)
 {
  do
  {
   if (fgets(linebuf, sizeof(linebuf), fd) == NULL)
   {
    fclose(fd);
    return 1;
   }
   coefline++;
   if ((er = strdecomp(linebuf, bufa)) == -2)
    exit( fprintf(stderr, "ERROR[line%d]: No RETURN in this line %d\n", __LINE__, coefline));
   if (er == -1) exit( fprintf(stderr, "ERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
  } while (bufa[0] == '#');

/* FilterFunctions */
  if (strcmp(bufa, "FilterFunctions:") == 0)
  {
   if (strstr(linebuf, "Lowpass") != NULL)
   {
    if (lowpass00 != 1)
     exit( fprintf(stderr, "ERROR[line%d] readcoef: Filter coefficient (line%d) mismatch (lowpass00=%d).\n", __LINE__, coefline, lowpass00));
   }
   else
    if (lowpass00 != 0)
     exit( fprintf(stderr, "ERROR[line%d] readcoef: Filter coefficient (line%d) mismatch (lowpass00=%d).\n", __LINE__, coefline, lowpass00));

   if (strstr(linebuf, "Highpass") != NULL)
   {
    if (highpass00 != 1)
     exit( fprintf(stderr, "ERROR[line%d] readcoef: Filter coefficient (line%d) mismatch (highpass00=%d).\n", __LINE__, coefline, highpass00));
   }
   else
    if (highpass00 != 0)
     exit( fprintf(stderr, "ERROR[line%d] readcoef: Filter coefficient (line%d) mismatch (highpass00=%d).\n", __LINE__, coefline, highpass00));

   if (strstr(linebuf, "Notch") != NULL)
   {
    if (notch00 < 1)
     exit( fprintf(stderr, "ERROR[line%d] readcoef: Filter coefficient (line%d) mismatch (notch00=%d).\n", __LINE__, coefline, notch00));
   }
   else
    if (notch00 != 0)
     exit( fprintf(stderr, "ERROR[line%d] readcoef: Filter coefficient (line%d) mismatch (notch00=%d).\n", __LINE__, coefline, notch00));

   if (strstr(linebuf, "Bandstop") != NULL)
   {
    if (bandstop00 != 1)
     exit( fprintf(stderr, "ERROR[line%d] readcoef: Filter coefficient (line%d) mismatch (bandstop00=%d).\n", __LINE__, coefline, bandstop00));
   }
   else
    if (bandstop00 != 0)
     exit( fprintf(stderr, "ERROR[line%d] readcoef: Filter coefficient (line%d) mismatch (bandstop00=%d).\n", __LINE__, coefline, bandstop00));
  }

/* Sampling Frequency */
  else
  if (strstr(linebuf, "Sampling Frequency") != NULL) smpf = atof(bufa);

/* Lowpass */
  else
  if (strstr(linebuf, "Lowpass") != NULL)
  {
   for (i=0; i<3; i++)
   {
    fgets(linebuf, sizeof(linebuf), fd); coefline++;
    if ((er = strdecomp(linebuf, buf)) == -1)
     exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));

    if (strstr(buf, "NumberOfPoles") != NULL)
    {
     if ((er = strdecomp(linebuf, buffer)) == -1)
      exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
     lowpass.pole = atoi(buffer);
     if ((er = strdecomp(linebuf, buffer)) == -1) /* for "x" */
      exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
     if ((er = strdecomp(linebuf, buffer)) == -1)
      exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
     poleA = atoi(buffer); /* usually poleA=2 */
    }
    else
    if (strstr(buf, "CutoffFrequency[Hz]") != NULL)
    {
     if ((er = strdecomp(linebuf, buffer)) == -1)
      exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
     lowpass.cutoff = atof(buffer);
    }
    else
    if (strstr(buf, "Decay[dB/oct]") != NULL)
    {
     if ((er = strdecomp(linebuf, buffer)) == -1)
      exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
     lowpass.decay = atof(buffer);
    }
   } /* for (i=0; i<3; i++) */

   for (i=0; i<lowpass.pole; i++)
   {
    fgets(linebuf, sizeof(linebuf), fd); coefline++;
    if ((er = strdecomp(linebuf, buf)) == -1)
     exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
    ggl[i] = atof(buf);
   }
   for (i=0; i<lowpass.pole; i++)
   {
    fgets(linebuf, sizeof(linebuf), fd); coefline++;
    for (j=0; j<poleA; j++)
    {
     if ((er = strdecomp(linebuf, buf)) == -1)
      exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
     aal[i][j] = atof(buf);
    }
   }
   for (i=0; i<lowpass.pole;i++)
   {
    fgets(linebuf, sizeof(linebuf), fd); coefline++;
    for (j=0; j<poleA; j++)
    {
     if ((er = strdecomp(linebuf, buf)) == -1)
      exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
     bbl[i][j] = atof(buf);
    }
   }
  } /* else if (strstr(linebuf, "Lowpass") != NULL) */

/* Highpass */
  else
  if (strstr(linebuf, "Highpass") != NULL)
  {
   for (i=0; i<3; i++)
   {
    fgets(linebuf, sizeof(linebuf), fd); coefline++;
    if ((er = strdecomp(linebuf, buf)) == -1)
     exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));

    if (strstr(buf, "NumberOfPoles") != NULL)
    {
     if ((er = strdecomp(linebuf, buffer)) == -1)
      exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
     highpass.pole = atoi(buffer);
     if ((er = strdecomp(linebuf, buffer)) == -1) /* for "x" */
      exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
     if ((er = strdecomp(linebuf, buffer)) == -1)
      exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
     poleA = atoi(buffer); /* usually poleA=2 */
    }
    else
    if (strstr(buf, "CutoffFrequency[Hz]") != NULL)
    {
     if ((er = strdecomp(linebuf, buffer)) == -1)
      exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
     highpass.cutoff = atof(buffer);
    }
    else
    if (strstr(buf, "Decay[dB/oct]") != NULL)
    {
     if ((er = strdecomp(linebuf, buffer)) == -1)
      exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
     highpass.decay = atof(buffer);
    }
   } /* for (i=0; i<3; i++) */

   for (i=0; i<highpass.pole; i++)
   {
    fgets(linebuf, sizeof(linebuf), fd); coefline++;
    if ((er = strdecomp(linebuf, buf)) == -1)
     exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
    ggh[i] = atof(buf);
   }
   for (i=0; i<highpass.pole; i++)
   {
    fgets(linebuf, sizeof(linebuf), fd); coefline++;
    for (j=0; j<poleA; j++)
    {
     if ((er = strdecomp(linebuf, buf)) == -1)
      exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
     aah[i][j] = atof(buf);
    }
   }
   for (i=0; i<highpass.pole;i++)
   {
    fgets(linebuf, sizeof(linebuf), fd); coefline++;
    for (j=0; j<poleA; j++)
    {
     if ((er = strdecomp(linebuf, buf)) == -1)
      exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
     bbh[i][j] = atof(buf);
    }
   }
  } /* else if (strstr(linebuf, "Highpass") != NULL) */

/* Notch */
  else
  if (strstr(linebuf, "Notch") != NULL)
  {
   fgets(linebuf, sizeof(linebuf), fd); coefline++;
   if ((er = strdecomp(linebuf, buf)) == -1)
    exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
   if (strstr(buf, "NumberOfNotchFilters") != NULL)
   {
    if ((er = strdecomp(linebuf, buffer)) == -1)
     exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
    notch.number = atoi(buffer);
   }
   else
    exit( fprintf(stderr, "readcoefERROR[line%d]: NumberOfNotchFilters should be first specified (line%d).\n", __LINE__, coefline));

   for (i=0; i<notch.number; i++)
   {
    for (i=0; i<3; i++)
    {
     fgets(linebuf, sizeof(linebuf), fd); coefline++;
     if ((er = strdecomp(linebuf, buf)) == -1)
      exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));

     if (strstr(buf, "NumberOfPoles") != NULL)
     {
      if ((er = strdecomp(linebuf, buffer)) == -1)
       exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
      notch.pole[i] = atoi(buffer);
      if ((er = strdecomp(linebuf, buffer)) == -1) /* for "x" */
       exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
      if ((er = strdecomp(linebuf, buffer)) == -1)
       exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
      poleA = atoi(buffer); /* usually poleA=4 */
     }
     else
     if (strstr(buf, "CenterFrequency[Hz]") != NULL)
     {
      if ((er = strdecomp(linebuf, buffer)) == -1)
       exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
      notch.freq[i] = atof(buffer);
     }
     else
     if (strstr(buf, "Decay[dB/oct]") != NULL)
     {
      if ((er = strdecomp(linebuf, buffer)) == -1)
       exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
      notch.decay[i] = atof(buffer);
     }
    } /* for (i=0; i<3; i++) */

    for (j=0; j<notch.pole[i]; j++)
    {
     fgets(linebuf, sizeof(linebuf), fd); coefline++;
     if ((er = strdecomp(linebuf, buf)) == -1)
      exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
     ggn[i][j] = atof(buf);
    } /* for (j=0; j<notch.pole[i]; j++) */
    for (j=0; j<notch.pole[i]; j++)
    {
     fgets(linebuf, sizeof(linebuf), fd); coefline++;
     for (k=0; k<poleA; k++)
     {
      if ((er = strdecomp(linebuf, buf)) == -1)
       exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
      aan[i][j][k] = atof(buf);
     }
    } /* for (j=0; j<notch.pole[i]; j++) */
    for (j=0; j<notch.pole[i]; j++)
    {
     fgets(linebuf, sizeof(linebuf), fd); coefline++;
     for (k=0; k<poleA; k++)
     {
      if ((er = strdecomp(linebuf, buf)) == -1)
       exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
      bbn[i][j][k] = atof(buf);
     }
    } /* for (j=0; j<notch.pole[i]; j++) */
   } /* for (i=0; i<notch.number; i++) */
  } /* else if (strstr(linebuf, "Notch") != NULL) */

/* Bandstop */
  else
  if (strstr(linebuf, "Bandstop") != NULL)
  {
   for (i=0; i<4; i++)
   {
    fgets(linebuf, sizeof(linebuf), fd); coefline++;
    if ((er = strdecomp(linebuf, buf)) == -1)
     exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));

    if (strstr(buf, "NumberOfPoles") != NULL)
    {
     if ((er = strdecomp(linebuf, buffer)) == -1)
      exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
     bandstop.pole = atoi(buffer);
     if ((er = strdecomp(linebuf, buffer)) == -1) /* for "x" */
      exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
     if ((er = strdecomp(linebuf, buffer)) == -1)
      exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
     poleA = atoi(buffer); /* usually poleA=4 */
    }
    else
    if (strstr(buf, "LowCutoffFrequency[Hz]") != NULL)
    {
     if ((er = strdecomp(linebuf, buffer)) == -1)
      exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
     bandstop.cutoff1 = atof(buffer);
    }
    else
    if (strstr(buf, "HighCutoffFrequency[Hz]") != NULL)
    {
     if ((er = strdecomp(linebuf, buffer)) == -1)
      exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
     bandstop.cutoff2 = atof(buffer);
    }
    else
    if (strstr(buf, "Decay[dB/oct]") != NULL)
    {
     if ((er = strdecomp(linebuf, buffer)) == -1)
      exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
     bandstop.decay = atof(buffer);
    }
   } /* for (i=0; i<4; i++) */

   for (i=0; i<bandstop.pole; i++)
   {
    fgets(linebuf, sizeof(linebuf), fd); coefline++;
    if ((er = strdecomp(linebuf, buf)) == -1)
     exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
    ggb[i] = atof(buf);
   }
   for (i=0; i<bandstop.pole; i++)
   {
    fgets(linebuf, sizeof(linebuf), fd); coefline++;
    for (j=0; j<poleA; j++)
    {
     if ((er = strdecomp(linebuf, buf)) == -1)
      exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
     aab[i][j] = atof(buf);
    }
   }
   for (i=0; i<bandstop.pole;i++)
   {
    fgets(linebuf, sizeof(linebuf), fd); coefline++;
    for (j=0; j<poleA; j++)
    {
     if ((er = strdecomp(linebuf, buf)) == -1)
      exit( fprintf(stderr, "readcoefERROR[line%d]: No items in this line %d\n", __LINE__, coefline));
     bbb[i][j] = atof(buf);
    }
   }
  } /* else if (strstr(linebuf, "Bandstop") != NULL) */

 } /* while (1) */

 fclose(fd);
}
