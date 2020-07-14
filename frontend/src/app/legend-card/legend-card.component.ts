import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { MatSlideToggleChange } from '@angular/material/slide-toggle';
import { Record, RecordsOneChannel } from '../chart/record';

@Component({
  selector: 'legend-card',
  templateUrl: './legend-card.component.html',
  styleUrls: ['./legend-card.component.scss'],
})
export class LegendCardComponent implements OnInit {
  @Input() time: string;
  @Input() date: string;
  @Input() power: number;

  @Input() recordsOneChannel: RecordsOneChannel;
  @Output() showChange = new EventEmitter<[string, boolean]>();

  checked = true;

  constructor() {}

  getAvg() {
    if (this.recordsOneChannel?.data.length == 0) return 0;
    let sum = 0;
    this.recordsOneChannel.data.forEach((record: Record) => {
      sum += record.value;
    });
    return (sum / this.recordsOneChannel.data.length).toPrecision(3);
  }

  getMax() {
    if (this.recordsOneChannel.data.length == 0) return 0;
    const maxRecord = this.recordsOneChannel.data.reduce(
      (record0: Record, record1: Record) => {
        return record0.value >= record1.value ? record0 : record1;
      }
    );
    return maxRecord.value.toPrecision(3);
  }

  getMin() {
    if (this.recordsOneChannel.data.length == 0) return 0;
    const maxRecord = this.recordsOneChannel.data.reduce(
      (record0: Record, record1: Record) => {
        return record0.value <= record1.value ? record0 : record1;
      }
    );
    return maxRecord.value.toPrecision(3);
  }

  toggled(event: MatSlideToggleChange) {
    this.showChange.emit([this.recordsOneChannel.name, event.checked]);
  }

  ngOnInit(): void {}
}
