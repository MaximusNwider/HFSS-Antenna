% Elevation patterns of a horizontal half-wave dipole over lossy ground
% Heights: h/λ = 0.01 and 0.25; Frequency default 10 MHz
%
% References:
% - Half-wave dipole elevation factor: Eθ ∝ cos((π/2)cosψ)/sinψ. 
%   See e.g., Balanis-style derivations and teaching notes. [AstroBaki] 
% - Fresnel TE reflection with magnetic media via impedances:
%   Γ_TE = (η2 cosθi - η1 cosθt)/(η2 cosθi + η1 cosθt). [Wikipedia Fresnel, Wave impedance]
% - Complex permittivity with conductivity: εc = εr - j σ/(ω ε0). [MathWorks doc]
% - Ground electrical parameters (HF): ITU-R P.527 / P.832 tables.
% - Example ferrite (Laird MP2106 family): μi≈650 and complex μr(f) curves in literature.

clear; clc;

%% ---------------- User controls ----------------
f        = 10e6;          % Hz (set any HF value)
heights  = [0.01, 0.25];  % h/λ values to plot
do_save  = false;         % set true to save figures

%% --------------- Constants & grids -------------
c0 = 299792458; eps0 = 8.854187817e-12; mu0 = 4*pi*1e-7;
omega = 2*pi*f;  lambda = c0/f;  k = 2*pi/lambda;

% Elevation angle ψ: 0° horizon -> 90° zenith
psi = linspace(deg2rad(0.1), deg2rad(89.9), 2000).';

%% --------------- Models ------------------------
% Half-wave thin-dipole elevation factor (normalized magnitude)
E_dip = @(psi) abs( cos((pi/2).*cos(psi)) ./ sin(psi) );   % [1]

% Complex relative permittivity with conductivity  (εc = εr - j σ/(ω ε0))  [3]
epsc = @(epsr, sigma) epsr - 1j*sigma/(omega*eps0);

% General TE Fresnel reflection (allows complex εr and μr)  [2]
% θi = incidence from the normal; n = sqrt(εr μr); η = sqrt(μ0 μr/(ε0 εr))
GammaTE = @(theta_i, epsr_c, mur_c) ...
    ( sqrt(mu0*mur_c./(eps0*epsr_c)).*cos(theta_i) - sqrt(mu0/eps0).*sqrt(1 - (sin(theta_i)./sqrt(epsr_c.*mur_c)).^2) ) ...
  ./ ( sqrt(mu0*mur_c./(eps0*epsr_c)).*cos(theta_i) + sqrt(mu0/eps0).*sqrt(1 - (sin(theta_i)./sqrt(epsr_c.*mur_c)).^2) );

% Free-space peak for normalization
E0 = E_dip(psi);  E0pk = max(E0);

%% --------------- Media (edit as needed) --------
% Typical HF ground values (representative):
%   Very poor soil: εr≈5,  σ≈0.001 S/m
%   Average ground: εr≈13, σ≈0.005 S/m
%   Sea water     : εr≈81, σ≈5 S/m
% Source: ITU-R P.527/P.832 typical curves.
grounds = struct( ...
  'name', {'Very poor soil','Average ground','Sea water', 'Ferrite ground plane'}, ...
  'epsr', {5.0, 13.0, 81.0, 12.0}, ...
  'sigma',{1e-3, 5e-3, 5.0, 0.0}, ...
  'mur',  {1+0j, 1+0j,   1+0j, (600 - 1j*150)} );   % example ferrite μr at ~10 MHz

%% --------------- Plot patterns -----------------
for h_over_lambda = heights
    h = h_over_lambda * lambda;
    theta_i = (pi/2) - psi;                   % incidence from normal
    figure('Color','w'); hold on; grid on; box on;
    for g = 1:numel(grounds)
        erc = epsc(grounds(g).epsr, grounds(g).sigma);
        mur = grounds(g).mur;
        Gamma = GammaTE(theta_i, erc, mur);
        phase = exp(-1j * 2 * k * h * cos(psi));
        Etot = E_dip(psi) .* abs(1 + Gamma .* phase);       % two-ray
        Rel_dB = 20*log10( Etot / (E0pk + 1e-15) + 1e-15 ); % vs free-space peak
        plot(rad2deg(psi), Rel_dB, 'LineWidth', 2, 'DisplayName', grounds(g).name);
    end
    yline(0,'k--','LineWidth',1,'DisplayName','Free-space peak (ref)');
    xlabel('Elevation angle \psi (deg)'); ylabel('Relative field (dB vs free-space peak)');
    title(sprintf('Horizontal Half-Wave Dipole @ %.1f MHz   h/\\lambda = %.2f', f/1e6, h_over_lambda));
    legend('Location','best'); xlim([0 90]);
    if do_save
        saveas(gcf, sprintf('dipole_patterns_%0.2flam_%0.1fMHz.png', h_over_lambda, f/1e6));
    end
end
