#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include "filt.h"

void passfilt(float *data, int datano, double gg[LoConst1], double aa[LoConst1][LoConst2], double bb[LoConst1][LoConst2], int nn)
{
    int    i,j,k;
    double  wx[2],wy[2],a[2],b[2],*tmp;
    double  g,x,y;

    if ((tmp = MALLOC(datano, double)) == NULL)
      exit (fprintf(stderr, "ERROR: memory allocation in passfilt; tmp MALLOC\n"));
    
    /*init*/
    for(i=0;i<datano;i++){
    tmp[i]=data[i];
    }
    /*start*/
    for(i=0;i<nn;i++){
      for(j=0;j<2;j++) {
        wx[j]=0.0;
	wy[j]=0.0;
	}
    a[0]=aa[i][0]; a[1]=aa[i][1];
    b[0]=bb[i][0]; b[1]=bb[i][1];
    g=gg[i];

    for(j=0;j<datano;j++){
    x=tmp[j];
    y=g*x+g*a[0]*wx[1]+g*a[1]*wx[0]-b[0]*wy[1]-b[1]*wy[0];
    wx[0]=wx[1]; wx[1]=x;
    wy[0]=wy[1]; wy[1]=y;
    tmp[j]=y;
    }
    }

    for(i=0;i<nn;i++){
      for(j=0;j<2;j++) {
        wx[j]=0.0;
	wy[j]=0.0;
	}
    a[0]=aa[i][0]; a[1]=aa[i][1];
    b[0]=bb[i][0]; b[1]=bb[i][1];
    g=gg[i];

    for(j=0;j<datano;j++){
    x=tmp[datano-1-j];
    y=g*x+g*a[0]*wx[1]+g*a[1]*wx[0]-b[0]*wy[1]-b[1]*wy[0];
    wx[0]=wx[1]; wx[1]=x;
    wy[0]=wy[1]; wy[1]=y;
    tmp[datano-1-j]=y;
    }
    }
  for(j=0;j<datano;j++) {
  data[j]=tmp[j];}

  FREEN(tmp);
  }
