function [tclose,impvel]=springmassdamperl(th,G,E,Patm)
deterministic=1;damping =1;
%Mean Beam dimensions
%L= Length of beam
%b= Width of beam

%Gauss distr
%th= thickness
%G= gap-size(m)
%electhick=0.1*G; 600E-9; thicnkness of pad
%E = Young's Modulus

%Beam properties
%M= effective Mass of system(kg)  
%K= Stiffness(N/m^2)
th=th*1e-6;
G=G*1e-6;
E=E*1e9;
%% user-defined
u0= 150;
electhick=3.5e-7;
%damping = 0 for no damping, 1 for compact model, 2 for veijola, 3 for Gallis-DSMC
% Patm= pressur in atm
rho_s=8910; % Nickel theory kg/m^3
L=510e-6;
b=123e-6;
L0=L;
w0=b;
eps0= 8.8542e-12;
A=w0*40E-6*1.2;

%stiffness
x=(L0+1.2*w0)/2;
c0=(8*(x/L0)^3-20*(x/L0)^2+14*(x/L0)-1);
Cm=12*rho_s*L0*w0*32/(4.73004^4*c0);
Ck=32*w0/L0^3/c0;
CVp=sqrt(8*32*w0/(L0^3*27*A*eps0*c0));

mfun=@(t) Cm*t; %mass
Kfun=@(t,E) Ck*E*t^3; %stiffness
Vpfun=@(t,E,g)CVp*t^1.5*g^1.5*E^0.5; %actuation voltage
 
M=mfun(th);
    K=Kfun(th,E);
    Vp=Vpfun(th,E,G);

Pressure=101325*Patm;
%% Equation 1
x0=[0 0]; %initial [x,x']
%{
% MX''+KX=eps*a/2*(u/(G-X))^2
reltol=1e-8; abstol=1e-8;
options = odeset('RelTol',reltol,'AbsTol',[abstol abstol]);
[T,X] = ode45(@mems_fun,[0 tmax],x0,options);
%}
X(1,1:2)=x0;T(1)=0.0;X(1,3)=0.0;
dt=1e-9;
%finite difference solve
t=1;
while X(t,1)< G-electhick
    time=(t-1)*dt;    T(t+1)=time;
    [dx,F_el,F_damp,Qf] = mems_fun(time,X(t,1:2),L,b,th,G,E,M,K,damping,u0,Pressure);
    X(t+1,1:2) = X(t,1:2) +dt*dx' ; %distance,velocity
    X(t+1,3)=dx(2);  %acceleration
    t=t+1;
end

tclose=max(T);impvel=max(X(:,2));
fprintf('HDF5:{"name": "tclose", "value": %f, "desc": "closing time"}:5FDH\n', tclose);
fprintf('HDF5:{"name": "impvel", "value": %f, "desc": "impact velocity"}:5FDH\n', impvel);
end
