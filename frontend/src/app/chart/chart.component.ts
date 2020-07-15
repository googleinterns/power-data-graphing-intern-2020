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
  private svgLine: d3.Selection<SVGGElement, unknown, HTMLElement, any>;
  private xAxis: d3.Selection<SVGGElement, unknown, HTMLElement, any>;
  private xScale: d3.ScaleLinear<number, number>;
  private yAxis: d3.Selection<SVGGElement, unknown, HTMLElement, any>;
  private yScale: d3.ScaleLinear<number, number>;

  // Chart size constants
  animationDuration = 500;
  chartHeight = 400;
  chartMargin = 50;
  chartPadding = 5;
  chartWidth = 1100;
  svgPadding = 10;
  timeFormat = (time: number) => {
    const timeParse = d3.timeParse('%Q');
    const timeFormat = d3.timeFormat('%M:%S.%L');

    const upperDate = timeParse(Math.floor(time / 1000).toString());
    const formattedTime = timeFormat(upperDate);
    return formattedTime;
  };

  constructor(private service: HttpService) {}

  ngOnInit(): void {
    this.initChart();
    this.loadRecords();
  }

  ngOnDestroy(): void {
    this.subscription.unsubscribe();
  }

  loadRecords(timespan?: number[]) {
    this.loading = true;
    this.subscription = this.service
      .getRecords('/data', this.strategy, timespan)
      .subscribe((response: RecordsResponse[]) => {
        this.records = response.map(
          (channel: RecordsResponse, index: number) => {
            const recordsOneChannel = {
              color: COLORS[index],
              data: channel.data.map((d: [number, number]) => {
                return {
                  time: d[0],
                  value: d[1],
                } as Record;
              }),
              focusDate: '',
              focusTime: '',
              focusPower: '',
              name: channel.name,
              show: true,
            };
            return recordsOneChannel;
          }
        );
        this.loading = false;
        this.updateChartDomain();
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
      .attr('width', this.chartWidth - this.chartMargin * 2)
      .attr('height', this.chartHeight)
      .attr('x', this.chartMargin)
      .attr('y', 0);

    // Create the chart variable: where both the chart and the brush take place
    this.svgChart = this.svg.append('g').attr('clip-path', 'url(#clip)');

    // Scales
    this.xScale = d3
      .scaleLinear()
      .domain(this.getTimeRange())
      .range([
        this.chartMargin + this.chartPadding,
        this.chartWidth - this.chartMargin - this.chartPadding,
      ]);

    this.yScale = d3
      .scaleLinear()
      .domain(this.getValueRange())
      .range([
        this.chartHeight - this.chartMargin - this.chartPadding,
        this.chartMargin + this.chartPadding,
      ]);

    // Create Axis
    this.xAxis = this.svg
      .append('g')
      .classed('x-axis', true)
      .attr('transform', `translate(0, ${this.chartHeight - this.chartMargin})`)
      .call(d3.axisBottom(this.xScale));

    this.yAxis = this.svg
      .append('g')
      .classed('y-axis', true)
      .attr('transform', `translate(${this.chartMargin},0)`)
      .call(d3.axisLeft(this.yScale));

    this.svgLine = this.svgChart.append('g');

    // Brush functionality
    this.brush = d3
      .brushX()
      .extent([
        [this.chartMargin, this.chartMargin],
        [
          this.chartWidth - this.chartMargin,
          this.chartHeight - this.chartMargin,
        ],
      ])
      .on('end', this.interactChart.bind(this));

    const setFocus = (container: d3.ContainerElement) => {
      // recover coordinate we need
      const mouseFocus = this.xScale.invert(d3.mouse(container)[0]);
      if (mouseFocus === undefined) return;

      const timeParse = d3.timeParse('%Q');
      const dateFormat = d3.timeFormat('%Y-%m-%d');
      const timeFormat = d3.timeFormat('%H:%M:%S.%L');

      const bisectLeft = d3.bisector((d: Record) => d.time).left;
      const bisectRight = d3.bisector((d: Record) => d.time).right;

      this.records.forEach((recordsOneChannel: RecordsOneChannel) => {
        const left = bisectLeft(recordsOneChannel.data, mouseFocus);
        const right = bisectRight(recordsOneChannel.data, mouseFocus);

        if (!recordsOneChannel.data[left] || !recordsOneChannel.data[right])
          return;
        const leftRecord = recordsOneChannel.data[left];
        const rightRecord = recordsOneChannel.data[right];

        const index =
          Math.abs(leftRecord.time - mouseFocus) >
          Math.abs(rightRecord.time - mouseFocus)
            ? right
            : left;
        const selectedData = recordsOneChannel.data[index];
        const upperDate = timeParse(
          Math.floor(selectedData.time / 1000).toString()
        );

        recordsOneChannel.focusTime =
          timeFormat(upperDate) + '.' + Math.floor(mouseFocus % 1000);
        recordsOneChannel.focusDate = dateFormat(upperDate);
        recordsOneChannel.focusPower = selectedData.value.toString();

        this.svgLine
          .select('.' + this.getChannelCircleClassName(recordsOneChannel.name))
          .attr('cx', this.xScale(selectedData.time))
          .attr('cy', this.yScale(selectedData.value));
      });
    };
    // Mouse over displaying text
    this.svgChart
      .append('g')
      .attr('class', 'brush')
      .call(this.brush)
      .on('mousemove', mousemove);

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
      .call(d3.axisBottom(this.xScale).ticks(7).tickFormat(this.timeFormat));
    this.yAxis
      .transition()
      .duration(this.animationDuration)
      .call(d3.axisLeft(this.yScale));

    this.records.forEach((recordsOneChannel: RecordsOneChannel) => {
      // if (!recordsOneChannel.show) return;
      if (!this.lines[recordsOneChannel.name]) {
        // Initialize focus line.
        const line = d3
          .line()
          .x((d: any) => this.xScale(d.time))
          .y((d: any) => this.yScale(d.value));
        this.lines[recordsOneChannel.name] = line;

        this.svgLine
          .append('path')
          .classed(this.getChannelLineClassName(recordsOneChannel.name), true)
          .attr('fill', 'none')
          .attr('stroke', recordsOneChannel.color)
          .attr('stroke-width', 2)
          .attr('d', line(recordsOneChannel.data as any))
          .attr('opacity', 0.4);

        this.svgLine
          .append('g')
          .append('circle')
          .classed(this.getChannelCircleClassName(recordsOneChannel.name), true)
          .style('fill', recordsOneChannel.color)
          .attr('stroke', recordsOneChannel.color)
          .attr('r', 2)
          .style('opacity', 1);
      } else if (recordsOneChannel.data.length) {
        // Reposition focus line.
        this.svgLine
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
    return 'line' + '-' + channel;
  }
  getChannelCircleClassName(channel: string) {
    return 'circle' + '-' + channel;
  }

  getTimeRange() {
    let min, max;
    this.records.forEach((recordsOneChannel: RecordsOneChannel) => {
      if (!recordsOneChannel.show) return;
      recordsOneChannel.data.forEach((record: Record) => {
        if (!min || record.time < min) min = record.time;
        if (!max || record.time > max) max = record.time;
      });
    });
    return [min, max];
  }
  getValueRange() {
    let min, max;
    this.records.forEach((recordsOneChannel: RecordsOneChannel) => {
      if (!recordsOneChannel.show) return;
      recordsOneChannel.data.forEach((record: Record) => {
        if (!min || record.value < min) min = record.value;
        if (!max || record.value > max) max = record.value;
      });
    });
    return [min, max];
  }

  showLine(event: [string, boolean]) {
    if (event[1]) {
      this.svgLine
        .select('.' + this.getChannelLineClassName(event[0]))
        .transition()
        .style('opacity', 0.4);
      this.svgLine
        .select('.' + this.getChannelCircleClassName(event[0]))
        .transition()
        .style('opacity', 1);
    } else {
      this.svgLine
        .select('.' + this.getChannelLineClassName(event[0]))
        .transition()
        .style('opacity', 0);
      this.svgLine
        .select('.' + this.getChannelCircleClassName(event[0]))
        .transition()
        .style('opacity', 0);
    }
    this.updateChartDomain();
  }
}
