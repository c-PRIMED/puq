% function for ode45
function [dx,F_el,F_damp,Qf] = mems_fun(t,x,L,b,th,G,E,M,K,damping,u0,Pressure)

wavetype=10;figdraw=0;mode=1; Beam='Fixed-Fixed';

Temp=300;
Rgas=287;muref=1.7894E-5;Tref = 297.0;wcoeff=0.77;
rho=Pressure/(Rgas*Temp);
mu=muref*(Temp/Tref)^wcoeff;  %viscosity based on temperature
lambda=mu/Pressure*sqrt(pi*Rgas*Temp/2); % mean-free-path (m)

rho_s=8910;
eps=8.8542E-12;% dielectric permittivity
a=L*b;        % Area(m^2)

%mechanical-impact between contact tabs Eqn(2)
%u=waveform(t,wavetype);
u=u0;

g=G-x(1); %current gap
F_el=(u/g)^2*eps*a/2;%electrostatic force
Kn=lambda./g;


% 1.3 frequency
if(strcmp(Beam,'Fixed-Free')==1)
    freq_beam=[1.8751 4.69409 7.8548];
elseif(strcmp(Beam,'Fixed-Fixed')==1)
    freq_beam=[4.7300 7.8532 10.9956];
end
I=b*th.^3/12;  % area moment of inertia for the beam
omegas=freq_beam.^2*sqrt(E*I/rho_s/b/th/L^4); % frequency, mode-1,2,3
omega=omegas(mode);

if(damping ==0)
    cf=0.0;
    Qf=0.0;
elseif(damping ==1)
    x1=b/g;x2=lambda/b;   %input non-dimensional parameters for cf
    %cf=compact(x1,x2,th);        %damping coefficient from compact model
    A1=10.39;B1=1.374;c1=3.1;d1=1.825;e1=0.966; % coefficients in the compact damping model
    cf=A1*x1.^c1.*th/(1+B1*x1.^d1*x2.^e1);
    Qf=rho_s*b*th*omega/cf;
elseif(damping==2) %Veijola 2004
    q=sqrt(1i*omega.*rho/mu);   % complex frequency
    sigmap=1.0;
    Qpr=12*mu/1i/omega/rho/g^3/q*(q*g ...
        -(2-q^2*sigmap*lambda*g)*tanh(q*g/2))/...
        (1+sigmap*lambda*q*tanh(q*g/2));
    squezec=12*mu*b^2./(Qpr.*Pressure*g^2)*omega;
    beta=sqrt(1i*squezec);
    Fbvb=L*b*Pressure./(1i*omega*g).*(2./beta.*tanh(beta/2)-1);
    zeta=real(Fbvb)/L./(2*rho_s*b*th*omega);
    Qf=abs(0.5./zeta);
    cf=rho_s*b*th*omega/Qf;
elseif(damping ==20)              %Veijola
    %%%%%%%% Veijola-99 %%%%%%%%%
    Qpr=1+9.638*(Kn)^1.159;
    squezec=12*mu*b^2./(Qpr.*Pressure*g^2)*omega;
    beta=sqrt(i*squezec);
    Fbvb=L*b*Pressure./(i*omega*g).*(2./beta.*tanh(beta/2)-1);
    zeta=real(Fbvb)/L./(2*rho_s*b*th*omega);
    Qf=abs(0.5./zeta);
    cf=rho_s*b*th*omega/Qf;
elseif(damping ==3)   %%%%%%%% Gallis-Torczynski (DSMC) model %%%%%%%%
    c1=(1+8.834.*Kn)./(1+5.118.*Kn);         %eqn(16)
    c2=(0.634+1.572.*Kn)./(1+0.537.*Kn);     %eqn(17)
    c3=(0.445+11.20.*Kn)./(1+5.510.*Kn);     %eqn(18)
    GammaG=mu*(b/g)^3.*(1+c1*6.*Kn).^(-1).*(1+3*c2*2*g/b+3*c3*(2*g/b).^2);
    zeta=GammaG./(2*rho_s*b*th*omega);
    Qf=0.5./zeta;
    cf=rho_s*b*th*omega/Qf;
end
F_damp=cf*x(2)*L;           %damping force

if(figdraw ==1)
    figure(1);hold on;
    plot(t*1e6,F_el*1e3,'r*');hold on;
    plot(t*1e6,F_damp*1e3,'b+');
    xlabel('time /mu s');ylabel('Fel and F_damp mN');
    legend('Electrostatic','Damping');
end

dx = zeros(2,1);    % a column vector
dx(1) = x(2);
dx(2) = -(K/M)*x(1)+F_el/M-F_damp/M;
