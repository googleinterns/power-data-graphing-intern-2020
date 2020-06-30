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

import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { HttpService } from '../services/http.service';
import * as d3 from 'd3';

import { Record } from '../record';
import { HttpResponse } from '@angular/common/http';

@Component({
  selector: 'main-chart',
  templateUrl: './chart.component.html',
  styleUrls: ['./chart.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class ChartComponent implements OnInit {
  // Data related variable
  loading = false;
  number = 600;
  records: Record[];
  strategy = 'max';
  zoomIn = false;

  // Chart d3 SVG Elements
  private brush: d3.BrushBehavior<unknown>;
  private line: d3.Line<[number, number]>;
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
  totalXDomain: Date[];
  animationDuration = 500;

  constructor(private service: HttpService) {}

  ngOnInit(): void {
    this.loadRecords(this.initChart.bind(this));
  }

  preprocess() {
    console.log('preprocessing');
  }

  loadRecords(chartFunction: () => void, timespan?: Date[]) {
    this.loading = true;
    this.service
      .getRecords('/data', this.strategy, timespan)
      .subscribe((response: HttpResponse<object>) => {
        this.records = Object.values(response.body).map(
          (d: [number, number, string]) => {
            return {
              time: this.timeParse(Math.floor(d[0] / 1000).toString()), // Ignoring microseconds in accord with the highest precision in JS
              value: d[1],
              source: d[2],
            } as Record;
          }
        );
        this.loading = false;

        this.totalXDomain = d3.extent(this.records, (d: Record) => d.time);
        chartFunction();
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
      .domain(d3.extent(this.records, (d: Record) => d.time))
      .range([this.chartPadding, this.chartWidth - this.chartPadding]);

    this.yScale = d3
      .scaleLinear()
      .domain(d3.extent(this.records, (d: Record) => d.value))
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

    const bisect = d3.bisector((d: Record) => d.time).left;

    // Create the circle that travels along the curve of chart
    const focus = this.svgChart
      .append('g')
      .append('circle')
      .style('fill', 'none')
      .attr('stroke', 'black')
      .attr('r', 4)
      .style('opacity', 0);

    // Create the text that travels along the curve of chart
    const focusText = this.svgChart
      .append('g')
      .append('text')
      .attr('opacity', 1)
      .attr('text-anchor', 'left')
      .attr('alignment-baseline', 'middle')
      .attr('font-size', '15px');

    // Draw lines
    this.line = d3
      .line()
      .x((d: any) => this.xScale(d.time))
      .y((d: any) => this.yScale(d.value));

    this.svgChart
      .append('path')
      // .datum(<any>this.records)
      .classed('line', true)
      .attr('fill', 'none')
      .attr('stroke', '#F29F05')
      .attr('stroke-width', 2)
      .attr('d', this.line(this.records as any))
      .attr('opacity', 0.4);

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
      focus.style('opacity', opacity);
      focusText.style('opacity', opacity);
    };

    const setFocus = (container: d3.ContainerElement) => {
      // recover coordinate we need
      const x0 = this.xScale.invert(d3.mouse(container)[0]);
      const i = bisect(this.records, x0, 1);
      const selectedData = this.records[i];

      focus
        .attr('cx', this.xScale(selectedData.time))
        .attr('cy', this.yScale(selectedData.value));
      focusText
        .html(
          `Time: ${this.timeFormat(selectedData.time)} - 
          Power: ${selectedData.value}`
        )
        .attr('x', this.xScale(selectedData.time) + 15)
        .attr('y', this.yScale(selectedData.value));
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
      });

    function mousemove() {
      setFocus(this);
    }
  }

  interactChart() {
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
    this.loadRecords(this.updateChartDomain.bind(this), selectedTimeSpan);

    this.svgChart.on('dblclick', () => {
      // // Reset scale domain
      this.zoomIn = false;
      this.loadRecords(this.updateChartDomain.bind(this));
    });
  }

  updateChartDomain() {
    const xExtent = d3.extent(this.records, (d) => d.time);
    const yExtent = d3.extent(this.records, (d) => d.value);

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
    this.svgChart
      .select('.line')
      .transition()
      .duration(this.animationDuration)
      .attr('d', this.line(this.records as any));
  }

  strategySwitch() {
    this.loadRecords(
      this.updateChartDomain.bind(this),
      this.zoomIn ? d3.extent(this.records, (d) => d.time) : null
    );
  }
}
