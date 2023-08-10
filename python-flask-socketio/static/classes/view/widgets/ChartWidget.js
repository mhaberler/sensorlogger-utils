/*
This class represents a chart
*/


let xMarks = [
    {
        type: 'annotation',
        from: 4,
        to: 4,
        label: 'eqk_01',
        link: 'https://google.com/',
        descr: 'Earthquake 01!',
    },
    {
        type: 'tor',
        from: 9.3,
        to: 18.5,
        label: 'tor_20',
        link: 'https://google.com/',
        descr: 'Tornado 20!',
    },
];

function annotationsPlugin(opts) {
    const { types } = opts;

    // TODO: use <template> + .cloneNode() ?
    function placeMark(u, mark, opts) {
        let markEl = document.createElement('div');
        markEl.classList.add('u-mark-x');

        let leftCss = Math.round(u.valToPos(mark.from, 'x'));
        let widthCss = mark.to > mark.from ? Math.round(u.valToPos(mark.to, 'x')) - leftCss : 0;

        Object.assign(markEl.style, {
            left: `${leftCss}px`,
            width: `${widthCss}px`,
            borderLeft: `${opts.width}px ${opts.dash ? 'dashed' : 'solid'} ${opts.stroke}`,
            borderRight: mark.to > mark.from ? `${opts.width}px ${opts.dash ? 'dashed' : 'solid'} ${opts.stroke}` : null,
            background: opts.fill,
        });

        let labelEl = document.createElement('div');
        labelEl.classList.add('u-mark-x-label');
        labelEl.textContent = mark.label;
        labelEl.title = mark.descr;

        Object.assign(labelEl.style, {
            border: `${opts.width}px ${opts.dash ? 'dashed' : 'solid'} ${opts.stroke}`,
            top: opts.align == 'top' ? 0 : '',
            bottom: opts.align == 'btm' ? 0 : '',
            background: opts.fill,
        });

        markEl.appendChild(labelEl);
        u.over.appendChild(markEl);
    }

    return {
        hooks: {
            drawClear: [
                (u) => {
                    for (let el of u.over.querySelectorAll('.u-mark-x'))
                        el.remove();
                    annotationBuffer.forEach(mark => {
                        const range = (mark.to - mark.from) > 0.1;
                        let o = opts.types[range ? "annotationspan" : "annotation"];

                        if (
                            mark.from >= u.scales.x.min &&
                            mark.from <= u.scales.x.max
                            ||
                            mark.to >= u.scales.x.min &&
                            mark.to <= u.scales.x.max
                            ||
                            mark.from <= u.scales.x.min &&
                            mark.to >= u.scales.x.max
                        ) {
                            placeMark(u, mark, o);
                        }
                    });
                }
            ],
        },
    };
}

class ChartWidget extends DataWidget {
    constructor(_isXY = false) {
        super();
        this.type = "chart";
        this.isXY = _isXY;
        this.data = []; // this is what contains the data ready for uplot
        this.data_available_xy = false; // this tells wheter this.data is ready for uplot for xy chart or not
        this.options = {
            title: "",
            width: undefined,
            height: undefined,
            scales: { x: { time: true }, y: {} },
            series: [{}],
            focus: { alpha: 1.0, },
            cursor: {
                lock: false,
                focus: { prox: 16, },
                sync: { key: window.cursorSync.key, setSeries: true }
            },
            legend: { show: false },
            plugins: [
                annotationsPlugin({
                    types: {
                        annotation: {
                            width: 2,
                            align: 'top',
                            stroke: 'rgb(255 193 7)',
                            fill: 'rgb(255 193 7 / 20%)',
                            dash: [5, 5],
                        },
                        annotationspan: {
                            width: 2,
                            align: 'btm',
                            stroke: 'rgb(76 175 80)',
                            fill: 'rgb(76 175 80 / 20%)',
                            dash: [5, 5],
                        },
                    }
                })
            ],
        }
        if (this.isXY) {
            this.data.push(null);
            this.options.mode = 2;
            delete this.options.cursor;
            this.options.scales.x.time = false;
        }
        this.forceUpdate = true;

        updateWidgetSize_(this);
    }
    destroy() {
        for (let s of this.series) s.destroy();
    }

    addSerie(_serie) {
        _serie.options._serie = _serie.name;
        _serie.options.stroke = ColorPalette.getColor(this.series.length).toString();
        _serie.options.fill = ColorPalette.getColor(this.series.length, 0.1).toString();
        if (this.isXY) _serie.options.paths = drawXYPoints;
        this.options.series.push(_serie.options);
        _serie.dataIdx = this.data.length;
        this.data.push([]);
        this.series.push(_serie);
        this.forceUpdate = true;
    }

    update() {
        // Update each series
        for (let s of this.series) s.update();
        if (app.isViewPaused && !this.forceUpdate) return;

        if (this.isXY) {
            if (this.forceUpdate) {
                this.data.length = 0;
                this.data.push(null);
                for (let s of this.series) {
                    s.dataIdx = this.data.length;
                    this.data.push(s.data);
                }
                this.id += "-" //DUMMY way to force update
                // triggerChartResize();
                this.forceUpdate = false;
            }
            else {
                for (let s of this.series) {
                    if (s.pendingData[0].length == 0) continue;
                    for (let i = 0; i < this.data[s.dataIdx].length; i++) {
                        this.data[s.dataIdx][i].push(...s.pendingData[i]);
                    }
                }
            }

            let elIsAlone = (el) => { return (el != null && el.length == 1) };

            this.data_available_xy = (this.data.length >= 2 && this.data[1] != null && this.data[1] != undefined
                && !(this.data[1].some(elIsAlone)));
        }
        else if (this.data[0].length == 0 || this.forceUpdate) {
            //Create data with common x axis
            let dataList = [];
            for (let s of this.series) dataList.push(s.data);
            this.data.length = 0;
            this.data = uPlot.join(dataList)
            this.id += "-" //DUMMY way to force update
            // triggerChartResize();
            this.forceUpdate = false;
        }
        else {
            //Iterate on all series, adding timestamps and values
            let dataList = [];
            for (let s of this.series) dataList.push(s.data);
            this.data.length = 0;
            this.data.push(...uPlot.join(dataList));
        }
    }
}