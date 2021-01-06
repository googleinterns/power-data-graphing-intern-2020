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

import { Component, Input, Output, EventEmitter } from '@angular/core';
import { MatSlideToggleChange } from '@angular/material/slide-toggle';
import { RecordsOneChannel } from '../chart/record';

@Component({
  selector: 'tr[legend-table-entry]',
  templateUrl: './legend-table-entry.component.html',
  styleUrls: ['./legend-table-entry.component.scss'],
})
export class LegendTableEntryComponent {
  @Input() recordsOneChannel: RecordsOneChannel;
  @Output() showChange = new EventEmitter<[number, boolean]>();

  checked = true;

  constructor() {}

  getAvg() {
    if (this.recordsOneChannel?.data.length == 0) return 'N/A';
    let sum = 0;
    for (const record of this.recordsOneChannel.data) {
      sum += record.value;
    }

    return (sum / this.recordsOneChannel.data.length).toPrecision(3).toString();
  }

  getMax() {
    if (this.recordsOneChannel.data.length == 0) return 'N/A';
    let max = this.recordsOneChannel.data[0].value;
    for (const record of this.recordsOneChannel.data) {
      if (record.value > max) max = record.value;
    }
    return max.toPrecision(3).toString();
  }

  getMin() {
    if (this.recordsOneChannel.data.length == 0) return 'N/A';
    let min = this.recordsOneChannel.data[0].value;
    for (const record of this.recordsOneChannel.data) {
      if (record.value < min) min = record.value;
    }
    return min.toPrecision(3).toString();
  }

  toggled(event: MatSlideToggleChange) {
    this.recordsOneChannel.show = event.checked;
    this.showChange.emit([this.recordsOneChannel.id, event.checked]);
  }
}
