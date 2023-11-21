import { Component, OnInit } from '@angular/core';
import {
  HttpService
} from '../services/http.service';
import { FileServiceService } from '../services/file-service.service';
import { Router } from '@angular/router';
import { Location } from '@angular/common';

@Component({
  selector: 'app-file-list',
  templateUrl: './file-list.component.html',
  styleUrls: ['./file-list.component.scss']
})
export class FileListComponent implements OnInit {
  fileList: string[] = [];
  displayList: string[] = [];
  selectedFilename = "";
  loading = false;
  loadingError = false;
  constructor(private service: HttpService, private readonly fileService: FileServiceService, private readonly location: Location, private readonly router: Router) {
  }

  updateUrl() {
    const url = this.router
      .createUrlTree([window.location.pathname], {
        queryParams: {
          'filename': this.selectedFilename,
        }
      }).toString();
    this.location.go(url);
  }

  ngOnInit(): void {
    this.fileService.filename.subscribe(filename => {
      this.selectedFilename = filename;
    });
  }

}
