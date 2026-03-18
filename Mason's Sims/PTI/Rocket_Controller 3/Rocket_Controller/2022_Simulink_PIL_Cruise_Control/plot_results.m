clear;
load('result_data.mat')


figure(1)
subplot(211)
plot(time,u,'b','LineWidth',2)
axis([0 Tsim -1 10])
grid
subplot(212)
plot(time,v,'b',time,v_ref,'--k','LineWidth',2)
axis([0 Tsim -1 7])
grid

