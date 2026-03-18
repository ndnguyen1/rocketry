function X_poly = get_poly_features(X, degree)
    % Generate polynomial features up the desired degree
    n = length(X);
    X_poly = 1;  % constant bias term
    
    for d = 1:degree
        combos = nchoosek(repmat(1:n, 1, d), d);
        combos = unique(sort(combos, 2), 'rows');
        for i = 1:size(combos, 1)
            term = prod(X(combos(i, :)));
            X_poly = [X_poly, term];
        end
    end
end
