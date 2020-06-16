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
  records: Record[];
  loading = false;

  // Chart d3 SVG Elements
  private xAxis: d3.Selection<SVGGElement, unknown, HTMLElement, any>;
  private xScale: d3.ScaleTime<number, number>;
  private yScale: d3.ScaleLinear<number, number>;
  private svgChart: d3.Selection<SVGGElement, unknown, HTMLElement, any>;
  private brush: d3.BrushBehavior<unknown>;

  // Chart size constants
  chartWidth = 1100;
  chartHeight = 700;
  chartPadding = 50;
  timeParse = d3.timeParse('%Q');
  timeFormat = d3.timeFormat('%H:%M:%S.%L');

  constructor(private service: HttpService) {}

  ngOnInit(): void {
    this.loading = true;
    this.service
      .getRecords('/data', 400, 'max')
      .subscribe((response: HttpResponse<Object>) => {
        this.records = Object.values(response.body).map(
          (d: [number, number, string]) => {
            return <Record>{
              // Ignoring microseconds in accord with the highest precision in JS
              time: this.timeParse(Math.floor(d[0] / 1000).toString()),
              value: d[1],
              source: d[2],
            };
          }
        );

        this.loading = false;
        this.createLineChart();
      });
  }

  createLineChart() {
    // Chart SVG Component
    const svg = d3
      .select('#chart-component')
      .append('svg')
      .attr('width', this.chartWidth)
      .attr('height', this.chartHeight);

    // Add a clipPath: everything out of this area won't be drawn.
    svg
      .append('defs')
      .append('svg:clipPath')
      .attr('id', 'clip')
      .append('svg:rect')
      .attr('width', this.chartWidth - this.chartPadding * 2)
      .attr('height', this.chartHeight)
      .attr('x', this.chartPadding)
      .attr('y', 0);

    // Create the chart variable: where both the chart and the brush take place
    this.svgChart = svg.append('g').attr('clip-path', 'url(#clip)');

    // Scales
    this.xScale = d3
      .scaleTime()
      .domain(d3.extent(this.records, (d: Record) => d.time))
      .range([this.chartPadding, this.chartWidth - this.chartPadding]);

    this.yScale = d3
      .scaleLinear()
      .domain([
        d3.min(this.records, (d: Record) => d.value),
        d3.max(this.records, (d: Record) => d.value),
      ])
      .range([this.chartHeight - this.chartPadding, this.chartPadding]);

    // Create Axis
    this.xAxis = svg
      .append('g')
      .classed('x-axis', true)
      .attr(
        'transform',
        `translate(0, ${this.chartHeight - this.chartPadding})`
      )
      .call(d3.axisBottom(this.xScale));
    svg
      .append('g')
      .classed('y-axis', true)
      .attr('transform', `translate(${this.chartPadding},0)`)
      .call(d3.axisLeft(this.yScale));

    // // Draw Area under the curve
    // this.svgChart
    //   .append('path')
    //   .datum(<any>this.records)
    //   .classed('area', true)
    //   .attr('fill', '#F2EEB3')
    //   .attr(
    //     'd',
    //     d3
    //       .area()
    //       .defined((d: any) => d.value >= 0)
    //       .x((d: any) => this.xScale(d.time))
    //       .y0(() => this.yScale.range()[0])
    //       .y1((d: any) => this.yScale(d.value))
    //   );

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

    this.svgChart
      .append('path')
      .datum(<any>this.records)
      .classed('line', true)
      .attr('fill', 'none')
      .attr('stroke', '#F29F05')
      .attr('stroke-width', 2)
      .attr(
        'd',
        d3
          .line()
          .x((d: any) => this.xScale(d.time))
          .y((d: any) => this.yScale(d.value))
      )
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
      .on('end', this.updateChart.bind(this));

    // Variable references for mouseover function
    const records = this.records;
    const xScale = this.xScale;
    const yScale = this.yScale;
    const timeFormat = this.timeFormat;
    // Mouse over displaying text
    this.svgChart
      .append('g')
      .attr('class', 'brush')
      .call(this.brush)
      .on('mouseover', mouseover) //this mouse over value display functionality
      .on('mousemove', mousemove)
      .on('mouseout', mouseout);

    // What happens when the mouse move -> show the annotations at the right positions.
    function mouseover() {
      focus.style('opacity', 1);
      focusText.style('opacity', 1);
    }

    function mousemove() {
      // recover coordinate we need
      const x0 = xScale.invert(d3.mouse(this)[0]);
      const i = bisect(records, x0, 1);
      const selectedData = records[i];

      focus
        .attr('cx', xScale(selectedData.time))
        .attr('cy', yScale(selectedData.value));
      focusText
        .html(
          `Time: ${timeFormat(selectedData.time)} - 
          Power: ${selectedData.value}`
        )
        .attr('x', xScale(selectedData.time) + 15)
        .attr('y', yScale(selectedData.value));
    }
    function mouseout() {
      focus.style('opacity', 0);
      focusText.style('opacity', 0);
    }
  }
  updateChart() {
    // What are the selected boundaries?
    const extent = d3.event.selection;

    // A function that set idleTimeOut to null
    let idleTimeout: number;
    // If no selection, back to initial coordinate. Otherwise, update X axis domain
    if (!extent) {
      if (!idleTimeout)
        setTimeout(() => {
          idleTimeout = null;
        }, 350); // This allows to wait a little bit
      return;
    } else {
      this.xScale.domain([
        this.xScale.invert(extent[0]),
        this.xScale.invert(extent[1]),
      ]);
      this.svgChart.select('.brush').call(this.brush.move, null); // This remove the grey brush area as soon as the selection has been done
    }
    // Update axis, line and area position
    this.updateDomain(1000);

    this.svgChart.on('dblclick', () => {
      // Reset x scale domain
      this.xScale.domain(d3.extent(this.records, (d) => d.time));
      // Reset axis, line and area position
      this.updateDomain(250);
    });
  }

  // Update area, domain, line positions in accord with new interval
  updateDomain(duration: number) {
    this.xAxis.transition().duration(duration).call(d3.axisBottom(this.xScale));
    this.svgChart
      .select('.line')
      .transition()
      .duration(duration)
      .attr(
        'd',
        d3
          .line()
          .x((d: any) => this.xScale(d.time))
          .y((d: any) => this.yScale(d.value))
      );
    this.svgChart
      .select('.area')
      .transition()
      .duration(duration)
      .attr(
        'd',
        d3
          .area()
          .defined((d: any) => d.value >= 0)
          .x((d: any) => this.xScale(d.time))
          .y0(() => this.yScale.range()[0])
          .y1((d: any) => this.yScale(d.value))
      );
  }
}
