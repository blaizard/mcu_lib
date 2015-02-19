// example 1 : 1d linear interpolation

// Volumes
x = [1, 10, 50, 100, 250, 500, 1000]
// Prices
y = [4.69, 4.19, 3.77, 3.43, 3.10, 2.78, 2.34]

MAX_X = 1000

// Linear interpolation
x_interpolation = linspace(1, MAX_X, 400)';
y_linear = linear_interpn(x_interpolation, x, y);

d = splin(x, y)
[y_spline, a, b] = interp(x_interpolation, x, y, d); 

// Model
// Digikey Model
model_x = [1, 100, 500, 1000, 10000]
model_y = [1, 0.731343284, 0.592750533, 0.498933902, 0.4]
model_weight = 0.5

function polynomial = lagrange_interp(X,Y,x)
    n = length(X);
    phi = ones(n,length(x));
    polynomial = zeros(1,length(x));
    
    // Construct table of differences
    for i = 1:n
    	for j = 1:n  
    		if i~=j then
    			phi(i,:) = phi(i,:) .* (x-X(j)) ./ (X(i)-X(j));
    		end
    	end
    end
    
    for i = 1:n
    	polynomial = polynomial + Y(i)*phi(i,:);
    end
endfunction

int_y = []
for i = 1:length(x_interpolation)
	int_y(i) = lagrange_interp(x, y, x_interpolation(i));
end

function [y] = interpolation(model_x, model_y, x)
    state = 0
    // Returns the y coordinate of the given x
    for i = 1:length(model_x)
        // If the value is already known, directly returns it
        if x == model_x(i) then
            y = model_y(i);
            return;
        end
        // x is included between i-1 and i
        if model_x(i) > x then
            break;
        end
    end
    // Make sure we have enough point to interpolate
    if i <= 2 then
        y = 0;
        return;
    end
    if i >= length(model_x) then
        y = 0;
        return;
    end

    save_x = x
    x = model_x(i-1)

    // Calculate the derivatives a i and i+1
    di = (model_y(i-2) - model_y(i)) / (model_x(i-2) - model_x(i));
    di1 = (model_y(i-1) - model_y(i+1)) / (model_x(i-1) - model_x(i+1));
    // Calculate the derivate at x
    d = di + (di1 - di)*(x - model_x(i-1)) / (model_x(i) - model_x(i-1));
    // Calculate y
    // f(x) = ax^2 + bx + c
    // f'(x) = 2ax + b
    // model_y(i-1) = a*model_x(i-1)^2 + b*model_x(i-1) + c
    // model_y(i) = a*model_x(i)^2 + b*model_x(i) + c
    // d = 2*a*x + b
    // b = d - 2*a*x
    // model_y(i) = a*model_x(i)^2 + (d - 2*a*x)*model_x(i) + c
    // c = model_y(i) - a*model_x(i)^2 - (d - 2*a*x)*model_x(i)
    // model_y(i-1) = a*model_x(i-1)^2 + (d - 2*a*x)*model_x(i-1) + model_y(i) - a*model_x(i)^2 - (d - 2*a*x)*model_x(i)
    // model_y(i-1) - model_y(i) - d*model_x(i-1) + d*model_x(i) = a*model_x(i-1)^2 - 2*a*x*model_x(i-1) - a*model_x(i)^2 + 2*a*x*model_x(i)

    a = (model_y(i-1) - model_y(i) - d*model_x(i-1) + d*model_x(i)) / (model_x(i-1)^2 - 2*x*model_x(i-1) - model_x(i)^2 + 2*x*model_x(i));
    b = d - 2*a*x
    c = model_y(i) - a*model_x(i)^2 - (d - 2*a*x)*model_x(i)

    // Need a 5th order equation with:
    // f(x) = ax^4 + bx^3 + cx^2 + dx + e (for model_y(i-1) and model_y(i))
    // f'(x) = 4ax^3 + 3bx^2 + 2cx + d (for di, di1 and d)
    // a*model_x(i-1)^4 + b*model_x(i-1)^3 + c*model_x(i-1)^2 + d*model_x(i-1) + e - model_y(i-1) = 0
    // a*model_x(i)^4 + b*model_x(i)^3 + c*model_x(i)^2 + d*model_x(i) + e - model_y(i) = 0
    // a*4*model_x(i-1)^3 + b*3*model_x(i-1)^2 + c*2*model_x(i-1) + d - di = 0
    // a*4*model_x(i)^3 + b*3*model_x(i)^2 + c*2*model_x(i) + d - di1 = 0
    // a*4*x^3 + b*3*x^2 + c*2*x + d - der = 0
    //
 
    A = [
        [model_x(i-1)^4,    model_x(i-1)^3,     model_x(i-1)^2,     model_x(i-1),   1];
        [model_x(i)^4,      model_x(i)^3,       model_x(i)^2,       model_x(i),     1];
        [4*model_x(i-1)^3,  3*model_x(i-1)^2,   2*model_x(i-1),     1,              0];
        [4*model_x(i)^3,    3*model_x(i)^2,     2*model_x(i),       1,              0];
        [4*x^3,             3*x^2,              2*x,                1,              0];
    ];
    B = [
        model_y(i-1);
        model_y(i);
        di;
        di1;
        d
    ];
    
   // C = B \ A
    
  //  a = 4.189D+10
  //  b = 84431767.
  //  c = 175465.35
  //  d = 416.94919
  //  e = 1.4940956
    
   x = save_x
    
 //  y = a*x^4 + b*x^3 + c*x^2 + d*x + e
  // printf("%f\n", y);
  // y = 1;
   // return
   // printf("%f\n", a)
   y = a*x*x + b*x + c
endfunction

// Volumes
x = [1, 10, 50, 100, 250, 500, 1000]
// Prices
y = [4.69, 4.19, 3.77, 3.43, 3.10, 2.78, 2.34]
// Known states derivatives, corresponds to [10, 50, 100, 250, 500]
xp = [(4.69 - 3.77) / (1 - 50), (4.19 - 3.43) / (10 - 100), (3.77 - 3.10) / (50 - 250), (3.43 - 2.78) / (100 - 500), (3.10 - 2.34) / (250 - 1000)]
weight = 1

int_y = []
for i = 1:length(x_interpolation)
    int_y(i) = interpolation(x, y, x_interpolation(i));
end

clf()

a = gca()
a.axes_visible = "on";
a.data_bounds = [1,0; MAX_X,5];
a.grid = [2,2];
//a.log_flags = "lnn" ;

// Linear interpolation
plot2d(x_interpolation, y_linear, style=2)
// Spline interpolation
plot2d(x_interpolation, y_spline, style=3)
// Lagrange interpolation
plot2d(x_interpolation, int_y, style=7)
// Original data
//plot2d(x, y, style=-9, strf="000")


