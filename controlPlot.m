function [] = controlPlot(problem, metric, output, format)

algorithms = {'Borg', 'eMOEA'};
work = getenv('WORK');
metricNames = {'Hypervolume', 'Generational Distance', 'Inverse Generational Distance', 'Spacing', 'Epsilon Indicator', 'Maximum Pareto Front Error', 'Runtime'};
steps = 3; % the number of grid locations along each axis
index = [1, 2]; % the index of the two parameters to plot

fig = figure();
set(fig, 'Position', [100, 100, 1000, 250]);

for k=1:length(algorithms)
    algorithm = algorithms{k};

    % read parameters ranges
    fid = fopen(strcat('./params/', algorithm, '_Params'), 'r');
    settings = textscan(fid, '%s %f %f');
    fclose(fid);

    % read parameters and metrics
    parameters = load(strcat('./params/', algorithm, '_Sobol'), '-ascii');
    metrics = load(strcat(work, '/', algorithm, '_', problem, '.average'), '-ascii');

    % compute average of points within each grid
    sum = zeros(steps+1, steps+1);
    count = zeros(steps+1, steps+1);
    entries = min(size(parameters, 1), size(metrics, 1));

    for i=1:entries
        index1 = round(steps * (parameters(i, index(1)) - settings{2}(index(1))) / (settings{3}(index(1)) - settings{2}(index(1)))) + 1;
        index2 = round(steps * (parameters(i, index(2)) - settings{2}(index(2))) / (settings{3}(index(2)) - settings{2}(index(2)))) + 1;
        sum(index1, index2) = sum(index1, index2) + metrics(i, metric);
        count(index1, index2) = count(index1, index2) + 1;
    end

    Z = zeros(steps+1, steps+1);
    for i=1:steps+1
        for j=1:steps+1
            if (count(i, j) > 0)
                Z(i, j) = sum(i, j) / count(i, j);
            end
        end
    end
    Z = Z';

    X = zeros(1, steps+1);
    Y = zeros(1, steps+1);
    for i=1:steps+1
        X(1, i) = (settings{3}(index(1)) - settings{2}(index(1)))*((i-1)/steps) + settings{2}(index(1));
        Y(1, i) = (settings{3}(index(2)) - settings{2}(index(2)))*((i-1)/steps) + settings{2}(index(2));
    end

    % save the results so we can scale all algorithms later
    allX(k,:,:) = X(:,:);
    allY(k,:,:) = Y(:,:);
    allZ(k,:,:) = Z(:,:);
end

for k=1:length(algorithms)
    algorithm = algorithms{k};
    X(:,:) = allX(k,:,:);
    Y(:,:) = allY(k,:,:);
    Z(:,:) = allZ(k,:,:);

    % generate contour plot
    h = subplot(length(algorithms)/2, 2, k);
    hold on;

    [C, h] = contourf(X, Y, Z, 50);
    set(h, 'LineColor', 'none');

    % adjust colormap so that red indicates best and values are normalized
    cmap = (colormap('jet')).^2;
    minM = 0;
    maxM = max(metrics(:, metric));

    % scale the colors
    if(metric == 1)
        caxis([min(min(min(allZ))) max(max(max(allZ)))])
        cmap = flipud(cmap);
        colormap(cmap);
    else
        caxis([min(min(min(allZ))) max(max(max(allZ)))]);
    end
    colorbar;

    % if Z is constant, contourf fails to render; fill background with Z's value
    if (isempty(C))
        cindex = round((size(cmap, 1)-1) * (Z(1, 1) - minM) / (maxM - minM))+1;
        set(gca, 'Color', cmap(cindex, :));
        set(gcf, 'InvertHardCopy', 'off');
    end

    set(gca, 'XTick', [500 1000]);
    title(gca, [algorithm]);
end

set(gcf, 'PaperPositionMode', 'auto');
saveas(fig, output, format);

