// Copyright 2020 Google LLC
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
// =============================================================================

import { Component, OnInit, OnDestroy, ViewEncapsulation } from '@angular/core';
import { Subscription } from 'rxjs';
import * as d3 from 'd3';
import {
  HttpService,
  STRATEGY,
  RecordsResponse,
} from '../services/http.service';
import { Record, COLORS, RecordsOneChannel } from './record';

@Component({
  selector: 'main-chart',
  templateUrl: './chart.component.html',
  styleUrls: ['./chart.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class ChartComponent implements OnInit, OnDestroy {
  // Bind strategy type
  strategyType = STRATEGY;

  // Bind Subscription
  subscription: Subscription;

  // Data related variable
  loading = false;
  number = 600;
  records: RecordsOneChannel[] = [];
  strategy = STRATEGY.AVG;
  zoomIn = false;

  // Chart d3 SVG Elements
  private brush: d3.BrushBehavior<unknown>;
  private lines: object = {};
  private svg: d3.Selection<SVGGElement, unknown, HTMLElement, any>;
  private svgChart: d3.Selection<SVGGElement, unknown, HTMLElement, any>;
  private xAxis: d3.Selection<SVGGElement, unknown, HTMLElement, any>;
  private xScale: d3.ScaleTime<number, number>;
  private yAxis: d3.Selection<SVGGElement, unknown, HTMLElement, any>;
  private yScale: d3.ScaleLinear<number, number>;

  // Chart size constants
  chartHeight = 400;
  chartPadding = 50;
  chartWidth = 1100;
  timeParse = d3.timeParse('%Q');
  timeFormat = d3.timeFormat('%H:%M:%S.%L');
  animationDuration = 500;
  svgPadding = 10;

  // Chart selection
  date = '';
  time = '';
  power = 0;

  constructor(private service: HttpService) {}

  ngOnInit(): void {
    this.initChart();
    this.loadRecords();
  }

  ngOnDestroy(): void {
    this.subscription.unsubscribe();
  }

  loadRecords(timespan?: Date[]) {
    this.loading = true;
    this.subscription = this.service
      .getRecords('/data', this.strategy, timespan)
      .subscribe((response: RecordsResponse[]) => {
        this.records = response.map(
          (channel: RecordsResponse, index: number) => {
            const recordsOneChannel = {
              color: COLORS[index],
              show: true,
              name: channel.name,
              data: channel.data.map((d: [number, number]) => {
                return {
                  time: this.timeParse(Math.floor(d[0] / 1000).toString()), // Ignoring microseconds in accord with the highest precision in JS
                  value: d[1],
                } as Record;
              }),
            };
            return recordsOneChannel;
          }
        );
        this.loading = false;
        this.updateChartDomain();
        console.log(this.records);
      });
  }

  initChart() {
    // Chart SVG Component
    this.svg = d3
      .select('#chart-component')
      .append('svg')
      .attr('width', this.chartWidth)
      .attr('height', this.chartHeight);

    // Add a clipPath: everything out of this area won't be drawn.
    this.svg
      .append('defs')
      .append('svg:clipPath')
      .attr('id', 'clip')
      .append('svg:rect')
      .attr('width', this.chartWidth - this.chartPadding * 2)
      .attr('height', this.chartHeight)
      .attr('x', this.chartPadding)
      .attr('y', 0);

    // Create the chart variable: where both the chart and the brush take place
    this.svgChart = this.svg.append('g').attr('clip-path', 'url(#clip)');

    // Scales
    this.xScale = d3
      .scaleTime()
      .domain(this.getTimeRange())
      .range([this.chartPadding, this.chartWidth - this.chartPadding]);

    this.yScale = d3
      .scaleLinear()
      .domain(this.getValueRange())
      .range([this.chartHeight - this.chartPadding, this.chartPadding]);

    // Create Axis
    this.xAxis = this.svg
      .append('g')
      .classed('x-axis', true)
      .attr(
        'transform',
        `translate(0, ${this.chartHeight - this.chartPadding})`
      )
      .call(d3.axisBottom(this.xScale));

    this.yAxis = this.svg
      .append('g')
      .classed('y-axis', true)
      .attr('transform', `translate(${this.chartPadding},0)`)
      .call(d3.axisLeft(this.yScale));

    const focusLine = this.svgChart
      .append('g')
      .append('line')
      .attr('stroke', 'black')
      .style('opacity', 0);

    // Brush functionality
    this.brush = d3
      .brushX()
      .extent([
        [this.chartPadding, this.chartPadding],
        [
          this.chartWidth - this.chartPadding,
          this.chartHeight - this.chartPadding,
        ],
      ])
      .on('end', this.interactChart.bind(this));

    const setFocusOpacity = (opacity: number) => {
      focusLine.style('opacity', opacity);
    };

    const setFocus = (container: d3.ContainerElement) => {
      // recover coordinate we need
      const mouseFocus = this.xScale.invert(d3.mouse(container)[0]);
      if (mouseFocus === undefined) return;
      focusLine
        .attr('x1', this.xScale(mouseFocus))
        .attr('y1', this.chartPadding)
        .attr('x2', this.xScale(mouseFocus))
        .attr('y2', this.chartHeight - this.chartPadding);
      this.date =
        `${mouseFocus.getFullYear()}-` +
        `${mouseFocus.getMonth()}-` +
        `${mouseFocus.getDay()}`;
      this.time =
        `${mouseFocus.getHours()}:` +
        `${mouseFocus.getMinutes()}:` +
        `${mouseFocus.getSeconds()}.` +
        `${mouseFocus.getMilliseconds()}`;

      this.power = 1024;
    };
    // Mouse over displaying text
    this.svgChart
      .append('g')
      .attr('class', 'brush')
      .call(this.brush)
      .on('mouseover', () => {
        setFocusOpacity(1);
      }) // this mouse over value display functionality
      .on('mousemove', mousemove)
      .on('mouseout', () => {
        setFocusOpacity(0);
        this.time = undefined;
        this.date = undefined;
        this.power = undefined;
      });

    function mousemove() {
      setFocus(this);
    }
  }

  private interactChart() {
    // What are the selected boundaries?
    const extent = d3.event.selection;
    if (!extent) return;
    const selectedTimeSpan = [
      this.xScale.invert(extent[0]),
      this.xScale.invert(extent[1]),
    ];
    // This remove the grey brush area as soon as the selection has been done
    this.svgChart.select('.brush').call(this.brush.move, null);

    // Update axis, line and area position, and load new data with the range
    this.zoomIn = true;
    this.loadRecords(selectedTimeSpan);

    this.svgChart.on('dblclick', () => {
      // // Reset scale domain
      this.zoomIn = false;
      this.loadRecords();
    });
  }

  private updateChartDomain() {
    const xExtent = this.getTimeRange();
    const yExtent = this.getValueRange();

    this.xScale.domain(xExtent);
    this.yScale.domain(yExtent);
    this.xAxis
      .transition()
      .duration(this.animationDuration)
      .call(d3.axisBottom(this.xScale));
    this.yAxis
      .transition()
      .duration(this.animationDuration)
      .call(d3.axisLeft(this.yScale));

    this.records.forEach((recordsOneChannel: RecordsOneChannel) => {
      if (!this.lines[recordsOneChannel.name]) {
        const line = d3
          .line()
          .x((d: any) => this.xScale(d.time))
          .y((d: any) => this.yScale(d.value));
        this.lines[recordsOneChannel.name] = line;

        this.svgChart
          .append('path')
          .classed(this.getChannelLineClassName(recordsOneChannel.name), true)
          .attr('fill', 'none')
          .attr('stroke', recordsOneChannel.color)
          .attr('stroke-width', 2)
          .attr('d', line(recordsOneChannel.data as any))
          .attr('opacity', 0.4);
      } else {
        this.svgChart
          .select('.' + this.getChannelLineClassName(recordsOneChannel.name))
          .transition()
          .duration(this.animationDuration)
          .attr(
            'd',
            this.lines[recordsOneChannel.name](recordsOneChannel.data as any)
          );
      }
    });
  }

  strategySwitch() {
    this.loadRecords(this.zoomIn ? this.getTimeRange() : null);
  }

  getChannelLineClassName(channel: string) {
    return 'line' + '_' + channel;
  }

  getTimeRange() {
    let min, max;
    this.records.map((recordsOneChannel: RecordsOneChannel) => {
      recordsOneChannel.data.forEach((record: Record) => {
        if (!min || record.time < min) min = record.time;
        if (!max || record.time > max) max = record.time;
      });
    });
    return [min, max];
  }
  getValueRange() {
    let min, max;
    this.records.map((recordsOneChannel: RecordsOneChannel) => {
      recordsOneChannel.data.forEach((record: Record) => {
        if (!min || record.value < min) min = record.value;
        if (!max || record.value > max) max = record.value;
      });
    });
    return [min, max];
  }

  buttonfn() {
    this.svg.selectAll('*').remove();
  }

  myprint(checked: boolean) {
    console.log(checked);
  }
}
