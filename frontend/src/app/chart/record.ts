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
  color: string;
  show: boolean;
  data: Record[];
  name: string;
  focusTime: string;
  focusDate: string;
  focusPower: string;
}

export const COLORS = [
  '#488f31',
  '#7ba542',
  '#a9ba59',
  '#d5d074',
  '#ffe692',
  '#fdc072',
  '#f8995e',
  '#de425b',
];
