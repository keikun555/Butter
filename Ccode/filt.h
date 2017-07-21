/* Header firle for LowPass, HighPass, Notch, BandPass, and BandStop filters */

#define LoConst1 36
#define LoConst2  2
#define HiConst1 LoConst1 /* 36 */
#define HiConst2 LoConst2 /* 2 */
#define NoConst1 50
#define NoConst2 LoConst1 /* 36 */
#define NoConst3  4
#define BsConst1 LoConst1 /* 36 */
#define BsConst2 NoConst3 /* 4 */

typedef struct 
        {
         float cutoff;
         float decay;
         int   pole;
        } Filter01rec, *Filter01;

typedef struct
        {
         int   number;
         float freq[NoConst1];
         float decay[NoConst1];
         int   pole[NoConst1];
        } Filter02rec, *Filter02;

typedef struct 
        {
         float cutoff1;
         float cutoff2;
         float decay;
         int   pole;
        } Filter03rec, *Filter03;

int lowpass00, highpass00, notch00, bandstop00;
float smpf;

Filter01rec lowpass;
Filter01rec highpass;
Filter02rec notch;
Filter03rec bandstop;

double ggl[LoConst1], ggh[HiConst1], ggn[NoConst1][NoConst2], ggb[36];
double aal[LoConst1][LoConst2], aah[HiConst1][HiConst2], aan[NoConst1][NoConst2][NoConst3], aab[BsConst1][BsConst2];
double bbl[LoConst1][LoConst2], bbh[HiConst1][HiConst2], bbn[NoConst1][NoConst2][NoConst3], bbb[BsConst1][BsConst2];
