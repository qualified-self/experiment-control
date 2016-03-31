



#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "edflib.h"


#define SMP_FREQ 2048




int main(int argc, char *argv[])
{
  int i, j,
      hdl,
      buf2[SMP_FREQ],
      chns;

  double buf[SMP_FREQ],
         q;



  chns = 2;

  hdl = edfopen_file_writeonly("sinus.bdf", EDFLIB_FILETYPE_BDFPLUS, chns);

  if(hdl<0)
  {
    printf("error: edfopen_file_writeonly()\n");

    return(1);
  }

  for(i=0; i<chns; i++)
  {
    if(edf_set_samplefrequency(hdl, i, SMP_FREQ))
    {
      printf("error: edf_set_samplefrequency()\n");

      return(1);
    }
  }

  for(i=0; i<chns; i++)
  {
    if(edf_set_physical_maximum(hdl, i, 3000.0))
    {
      printf("error: edf_set_physical_maximum()\n");

      return(1);
    }
  }

  for(i=0; i<chns; i++)
  {
    if(edf_set_digital_maximum(hdl, i, 8388607))
    {
      printf("error: edf_set_digital_maximum()\n");

      return(1);
    }
  }

  for(i=0; i<chns; i++)
  {
    if(edf_set_digital_minimum(hdl, i, -8388608))
    {
      printf("error: edf_set_digital_minimum()\n");

      return(1);
    }
  }

  for(i=0; i<chns; i++)
  {
    if(edf_set_physical_minimum(hdl, i, -3000.0))
    {
      printf("error: edf_set_physical_minimum()\n");

      return(1);
    }
  }

  if(edf_set_label(hdl, 0, "sinus"))
  {
    printf("error: edf_set_label()\n");

    return(1);
  }

  if(edf_set_label(hdl, 1, "ramp"))
  {
    printf("error: edf_set_label()\n");

    return(1);
  }

  for(i=0; i<chns; i++)
  {
    if(edf_set_physical_dimension(hdl, i, "mV"))
    {
      printf("error: edf_set_physical_dimension()\n");

      return(1);
    }
  }

  for(j=0; j<10; j++)
  {
    for(i=0; i<SMP_FREQ; i++)
    {
      q = M_PI * 2.0;
      q /= SMP_FREQ;
      q *= i;
      q = sin(q);
      q *= 3000.0;
      buf[i] = q;
    }

    if(edfwrite_physical_samples(hdl, buf))
    {
      printf("error: edfwrite_physical_samples()\n");

      return(1);
    }

    for(i=0; i<SMP_FREQ; i++)
    {
      buf[i] = -3000.0 + (i * 2.9296875);
    }

    if(edfwrite_physical_samples(hdl, buf))
    {
      printf("error: edfwrite_physical_samples()\n");

      return(1);
    }
  }

  for(j=0; j<10; j++)
  {
    for(i=0; i<SMP_FREQ; i++)
    {
      q = M_PI * 2.0;
      q /= SMP_FREQ;
      q *= i;
      q = sin(q);
      q *= 8388607.0;
      buf2[i] = q;
    }

    if(edfwrite_digital_samples(hdl, buf2))
    {
      printf("error: edfwrite_digital_samples()\n");

      return(1);
    }

    for(i=0; i<SMP_FREQ; i++)
    {
      buf2[i] = -8388608 + (i * 8192);
    }

    if(edfwrite_digital_samples(hdl, buf2))
    {
      printf("error: edfwrite_digital_samples()\n");

      return(1);
    }
  }

  edfwrite_annotation_latin1(hdl, 0LL, -1LL, "Recording starts");

  edfwrite_annotation_latin1(hdl, 200000LL, -1LL, "Recording ends");

  edfclose_file(hdl);

  return(0);
}




















