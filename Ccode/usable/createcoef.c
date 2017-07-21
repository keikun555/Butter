#include <stdio.h>
#include <math.h>
#include "filt.h"

extern void lowcoef ();
extern void highcoef ();
extern void notchcoef (int);
extern void bandstopcoef ();

void createcoef()
{
 int i, j, k, l, m, n, mm, nn, nnh, nnl;
 float aa, bb, cc;

 if (lowpass00 != 0) lowcoef();
 if (highpass00 != 0) highcoef();
 if (notch00 != 0)
 {
  for (i=0; i<notch.number; i++) notchcoef(i);
 }
 if (bandstop00 != 0) bandstopcoef();
}
