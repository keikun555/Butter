#include <stdlib.h>
#include <math.h>
#include "filt.h"
#include <stdio.h>

extern void stopfilt (float *, int, double *, double (*)[NoConst3], double (*)[NoConst3], int);
extern void passfilt (float *, int, double *, double (*)[LoConst2], double (*)[LoConst2], int);

void applyfilter(float *data, int datano)
{
 int i, j, k, l, m, n, expdatano;
 float *tmp = NULL;

 expdatano = 0.3 * datano;
 /*if ((tmp = MALLOC(datano+expdatano, float)) == NULL)
   exit (fprintf(stderr, "ERROR: memory allocation in applyfilt; tmp MALLOC\n"));*/

 for (i=0; i<datano; i++) tmp[i] = data[i];
 for (i=0; i<expdatano; i++) tmp[datano+i] = data[datano-i-1];

/***** Lowpass *****/
 if (lowpass00 != 0) passfilt(tmp, datano+expdatano, ggl, aal, bbl, lowpass.pole);
/***** Highpass ****/
 if (highpass00 != 0) passfilt(tmp, datano+expdatano, ggh, aah, bbh, highpass.pole);
/****** Notch ******/
 if (notch00 != 0)
  for (i=0; i<notch.number; i++)
   stopfilt(tmp, datano+expdatano, ggn[i], aan[i], bbn[i], notch.pole[i]);
/***** Bandstop *****/
 if (bandstop00 != 0) stopfilt(tmp, datano+expdatano, ggb, aab, bbb, bandstop.pole);

 for (i=0; i<datano; i++) data[i] = tmp[i];

 FREEN(tmp);
}
