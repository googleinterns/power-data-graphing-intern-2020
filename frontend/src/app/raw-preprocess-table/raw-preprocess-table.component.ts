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
  fileinfo: { name: string; preprocessed: boolean; loading: boolean }[];

  constructor(private service: HttpService) {}

  ngOnInit(): void {
    this.loadFilenames();
  }

  loadFilenames() {
    this.subscription = this.service
      .getFileInfo('/fileinfo')
      .pipe(
        catchError((error: HttpErrorResponse) => {
          this.message.emit(error.message);
          this.loading = false;
          return throwError(error);
        })
      )
      .subscribe((response: ResponseFileInfo[]) => {
        this.fileinfo = response.map((singleFileInfo: ResponseFileInfo) => ({
          name: singleFileInfo.name,
          preprocessed: singleFileInfo.preprocessed,
          loading: false,
        }));
      });
  }

  preprocess(file: { name: string; preprocessed: boolean; loading: boolean }) {
    file.loading = true;
    this.service
      .preprocess('/data', file.name)
      .pipe(
        catchError((error: HttpErrorResponse) => {
          this.loading = false;
          this.message.emit(error.message);
          return throwError(error);
        })
      )
      .subscribe(() => {
        file.loading = false;
        file.preprocessed = true;
      });
  }

  showSpinner(loading: boolean) {
    return loading ? 1 : 0;
  }

  showPreprocess(preprocessed: boolean) {
    return preprocessed ? 'yes' : 'no';
  }
}
