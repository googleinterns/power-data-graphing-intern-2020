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
import { MatCheckboxChange } from '@angular/material/checkbox';
import { RecordsOneChannel } from '../chart/record';

@Component({
  selector: 'legend-table',
  templateUrl: './legend-table.component.html',
  styleUrls: ['./legend-table.component.scss'],
})
export class LegendTableComponent {
  @Input() records: RecordsOneChannel[] = [];
  @Output() showChange = new EventEmitter<[number, boolean]>();
  @Output() showAllChange = new EventEmitter<boolean>();

  constructor() {}

  showLine(event: [number, boolean]) {
    this.showChange.emit(event);
  }

  isAllSelected(): boolean {
    return (
      this.records.length > 0 &&
      this.records.every((record) => record.show)
    );
  }

  isPartiallySelected(): boolean {
    return (
      this.records.some((record) => record.show) && !this.isAllSelected()
    );
  }

  toggleAll(event: MatCheckboxChange) {
    this.setAll(event.checked);
  }

  setAll(show: boolean) {
    for (const record of this.records) {
      record.show = show;
    }
    this.showAllChange.emit(show);
  }
}
