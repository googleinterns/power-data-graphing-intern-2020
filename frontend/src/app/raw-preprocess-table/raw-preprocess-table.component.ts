import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { HttpService, ResponseFileInfo } from '../services/http.service';
import { Subscription, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { HttpErrorResponse } from '@angular/common/http';

@Component({
  selector: 'raw-preprocess-table',
  templateUrl: './raw-preprocess-table.component.html',
  styleUrls: ['./raw-preprocess-table.component.scss'],
})
export class RawPreprocessTableComponent implements OnInit {
  @Output() message = new EventEmitter<string>();
  subscription: Subscription;
  loading = false;
  fileinfo: ResponseFileInfo[];

  constructor(private service: HttpService) {}

  ngOnInit(): void {
    this.loadFilenames();
  }

  loadFilenames() {
    this.subscription = this.service
      .getFileInfo('/fileinfo')
      .pipe(
        catchError((error: HttpErrorResponse) => {
          this.message.emit(error.error);
          this.loading = false;
          return throwError(error);
        })
      )
      .subscribe((response: ResponseFileInfo[]) => {
        this.fileinfo = response;
        this.loading = false;
      });
  }
}
