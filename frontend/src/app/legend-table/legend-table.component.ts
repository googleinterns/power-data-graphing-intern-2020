import { Component, Input, Output, EventEmitter } from '@angular/core';
import { RecordsOneChannel } from '../chart/record';

@Component({
  selector: 'legend-table',
  templateUrl: './legend-table.component.html',
  styleUrls: ['./legend-table.component.scss'],
})
export class LegendTableComponent {
  @Input() records: RecordsOneChannel[] = [];
  @Output() showChange = new EventEmitter<[number, boolean]>();

  constructor() {}

  showLine(event: [number, boolean]) {
    this.showChange.emit(event);
  }
}
