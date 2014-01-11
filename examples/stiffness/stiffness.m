function K=stiffness(E,nu,sigma,L,b,h,xi,eta);
%
% author: Deborah Sulsky <sulsky@math.unm.edu>
%
% Use units g mm and msec --> stress in MPa
%
% Material properties (example values given)
%
% E=180.e3 % Young's modulus ( MPa)
% nu=0.3 % Poisson's ratio (dimensionless)
% sigma=10 % residual stress ( MPa)
%
% Device dimensions
%
% L=.382;     % length (mm)
% b=.12;      % width (mm)
% h=0.00207;  % thickness (mm)
%
% Dimensionless position of the measurement (xi, eta)
% xi=x/L  eta=y/L  where x is in [0, L] and y is in [-b/2, b/2]
% xi=0.5
% eta=0 for measurement at the center, eta=b/2/L for measurement at the edge
%
alpha=h/L;  % aspect ratio
% R^2=12*sigtilde/Etilde, r=R/alpha  (dimensionless residual stress)
Etilde=E/(1-nu^2);
sigtilde=sigma*(1-nu);
R=sqrt(12*sigtilde/Etilde);
r=R/alpha;
if(abs(r)<.000005)
    a=xi.*(1-xi);
    a0=a.^3;
    a1=a/10;
    s=sign(sigtilde);
    w=(a0/(3*alpha^3)).*(1-s.*a1*r.^2+a1/840.*(41*a+11).*r.^4);
else
    D=-2+2*cosh(r)-r.*sinh(r);
    k1=(r.*(1-xi).*sinh(r)+cosh(r.*xi)+1-cosh(r)-cosh(r.*(1-xi)))./(D*alpha^3);
    k2=(cosh(r.*(1-xi))-1+(sinh(r))./r+(1-xi).*(1-cosh(r))-(sinh(r.*(1-xi)))./r-(sinh(r.*xi))./r)./(D*alpha^3);
    w=k1.*((sinh(r.*xi))./r - xi)./(r.^2)+k2.*(cosh(r.*xi)-1)./(r.^2);
end
v=(eta.^2.*(1-xi).*xi/alpha^3)./(2*(1-nu)+r.^2.*eta.^2);
K=Etilde*b*1.e3/12./(w+v);
fprintf('HDF5:{"name": "K", "value": %.16g, "desc": "stiffness"}:5FDH\n', K);
