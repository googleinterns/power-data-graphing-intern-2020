import { Component, Input, Output, EventEmitter } from '@angular/core';
import { MatSlideToggleChange } from '@angular/material/slide-toggle';
import { RecordsOneChannel } from '../chart/record';

@Component({
  selector: 'tr[legend-card]',
  templateUrl: './legend-card.component.html',
  styleUrls: ['./legend-card.component.scss'],
})
export class LegendCardComponent {
  @Input() recordsOneChannel: RecordsOneChannel;
  @Output() showChange = new EventEmitter<[string, boolean]>();

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
    this.showChange.emit([this.recordsOneChannel.name, event.checked]);
  }
}
