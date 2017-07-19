#include <math.h>
#include <filt.h>

extern void bcoef (double, double *, double (*)[2], double (*)[2], int *, double *);

void lowcoef()
{
	static double pai=3.14159265358979324;
	double  sin(),atan();
	double  th,wp,ar,ar1,b1,b2,cd,e;
	double  gg1[LoConst1],aa1[LoConst1][LoConst2],bb1[LoConst1][LoConst2],c;
	int    i,nn;

	e = lowpass.decay / 2.0;
	bcoef(e, gg1, aa1, bb1, &nn, &c);
	wp = 2.0 * pai * lowpass.cutoff / smpf;
	th=2.0*atan(c/2.0);
	ar=sin((th-wp)/2.0)/sin((th+wp)/2.0);
	ar1=(1.0-ar)*(1.0-ar);
	for(i=0;i<nn;i++){
		b1=bb1[i][0]; 
		b2=bb1[i][1];
		cd=1.0-b1*ar+b2*ar*ar;
		ggl[i]=gg1[i]*ar1/cd;
		bbl[i][0]=((1.0+ar*ar)*b1-2.0*ar*(b2+1.0))/cd;
		bbl[i][1]=(ar*ar-b1*ar+b2)/cd;
		aal[i][0]=aa1[i][0];
		aal[i][1]=aa1[i][1];
	}
        lowpass.pole=nn;
}
