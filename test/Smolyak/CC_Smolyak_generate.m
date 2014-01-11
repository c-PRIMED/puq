function CC_Smolyak_generate(dim,level)
%
% CC_Smolyak_generate(dim, level)
%
% This file generates the Smolyak cubature in arbitray dimension "dim" for
% a given level of accuracy "level", and writes the output in a file 
% CCSmolyak_d X s Y.dat, where X, Y stand for dim and level, respectively.
%
% File created and tested by Dongbin Xiu, 2004.
%
    d = dim;  s = level;
    fname = sprintf('CCsmolyak_d%ds%d.dat',d,s);
    fp = fopen(fname, 'w');
    q = d+s;
    [z,w] = PzPw_Smolyak(d,q);
    [row, col] = size(z);
    fprintf(fp, '  %d\n', row);
    for i=1:row
      for j = 1:col
        fprintf(fp, '%23.16e  ', z(i,j));
      end
      fprintf(fp, '  %23.16e', w(i));
      fprintf(fp,'\n');
    end
    fprintf(fp,'\n');
    fclose(fp);

