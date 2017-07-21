#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include "filt.h"
void ffiltsub(double, double *, double, double *, double *, double *);

void stopfilt(float *data, int datano, double gg[NoConst2] , double aa[NoConst2][NoConst3], double bb[NoConst2][NoConst3], int nn)
{
    int    i,j,k;
    double  w[5],a[4],b[4],*tmp;
    double  g,x,y;

    if ((tmp = MALLOC(datano, double)) == NULL)
      exit (fprintf(stderr, "ERROR: memory allocation in ffilt; tmp MALLOC\n"));
    
    /*init*/
    for(i=0;i<datano;i++){
    tmp[i]=data[i];}
    /*start*/
    for(i=0;i<nn;i++){
      for(j=0;j<5;j++) {
        w[j]=0.0;
	}
    a[0]=aa[i][0]; a[1]=aa[i][1];
    a[2]=aa[i][2]; a[3]=aa[i][3];
    b[0]=bb[i][0]; b[1]=bb[i][1];
    b[2]=bb[i][2]; b[3]=bb[i][3];
    g=gg[i];
    for(j=0;j<datano;j++){
    x=tmp[j];
    ffiltsub(x,&y,g,a,b,w);
    tmp[j]=y;
    }
    }
    for(i=0;i<nn;i++){
      for(j=0;j<5;j++) {
        w[j]=0.0;
	}
    a[0]=aa[i][0]; a[1]=aa[i][1];
    a[2]=aa[i][2]; a[3]=aa[i][3];
    b[0]=bb[i][0]; b[1]=bb[i][1];
    b[2]=bb[i][2]; b[3]=bb[i][3];
    g=gg[i];
    for(j=0;j<datano;j++){
    x=tmp[datano-1-j];
    ffiltsub(x,&y,g,a,b,w);
    tmp[datano-1-j]=y;
    }
    }
  for(j=0;j<datano;j++) {
  data[j]=tmp[j];}

  FREEN(tmp);
  }

void ffiltsub(x,y,g,a,b,w)
double x,*y,g,a[],b[],w[];
{
  w[4]=g*x-b[0]*w[3]-b[1]*w[2]-b[2]*w[1]-b[3]*w[0];
  *y=w[4]+a[0]*w[3]+a[1]*w[2]+a[2]*w[1]+a[3]*w[0];
  w[0]=w[1];
  w[1]=w[2];
  w[2]=w[3];
  w[3]=w[4];
  }
