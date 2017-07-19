#include <math.h>

void bcoef(double e, double gg[], double aa[][2], double bb[][2], int *n, double *omc)
{
	static double pai=3.14159265358979324;
	double  sin(),log10(),pow();
	double  bk,ak,c,dp,dpn,om1,om2,p;
	double  th,wp,ar,ar1,b1,b2;
	int    i,nn;

	om1=0.3*pai;
	om2=2.0*om1;
	p=-e/10.0+log10(0.9999);
	p=pow(10.0,p);
	c=((1.0/0.9999)*(1.0/0.9999)-1.0)/((1.0/p)*(1.0/p)-1.0);
	c=log10(c)/(2.0*log10(om1/om2));
	nn=(int)c+1;
	if(nn%2 != 0) nn=nn+1;
	p=log10(om1)-log10((1.0/0.9999)*(1.0/0.9999)-1.0)/(2.0*(float)nn);
	c=pow(10.0,p);
	/* Coef */
	dp=pai/(2.0*(float)nn);
	nn=nn/2;
	for(i=1;i<=nn;i++){
		dpn=dp*(float)(2*i-1);
		ak=c*sin(dpn);
		bk=1.0+ak+c*c/4.0;
		gg[i-1]=c*c/(4.0*bk);
		aa[i-1][0]=2.0;
		aa[i-1][1]=1.0;
		bb[i-1][0]=2.0*(c*c/4.0-1.0)/bk;
		bb[i-1][1]=(1.0-ak+c*c/4.0)/bk;
	}
	*n=nn;
	*omc=c;
}
