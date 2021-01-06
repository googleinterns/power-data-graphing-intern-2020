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

/**
 * Power data interface
 */
export interface Record {
  time: number;
  value: number;
}

export interface RecordsOneChannel {
  id: number;
  color: string;
  show: boolean;
  data: Record[];
  name: string;
  focusPower: string;
}

export const COLORS = [
  '#4285f4', '#DB4437', '#F4B400', '#0F9D58', '#FF00BF', '#8E24AA', '#1A237E',
  '#4DD0E1', '#26A69A', '#FFEB3B', '#00B3E6', '#64FFDA', '#3366E6', '#999966',
  '#99FF99', '#B34D4D', '#80B300', '#809900', '#E6B3B3', '#6680B3', '#66991A',
  '#FF99E6', '#CCFF1A', '#FF1A66', '#E6331A', '#33FFCC', '#66994D', '#B366CC',
  '#4D8000', '#B33300', '#CC80CC', '#66664D', '#991AFF', '#E666FF', '#4DB3FF',
  '#1AB399', '#E666B3', '#33991A', '#CC9999', '#B3B31A', '#00E680', '#4D8066',
  '#809980', '#E6FF80', '#1AFF33', '#999933', '#FF3380', '#CCCC00', '#66E64D',
  '#4D80CC', '#9900B3', '#E64D66', '#4DB380', '#FF4D4D', '#99E6E6', '#6666FF',
];

export enum STRATEGY {
  AVG = 'avg',
  MAX = 'max',
  MIN = 'min',
}
