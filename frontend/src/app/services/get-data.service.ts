import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root',
})
export class GetDataService {
  private url = 'http://127.0.0.1:5000/data';
  loading = false;

  constructor(private http: HttpClient) {}

  getRecords() {
    return this.http.get(this.url, {
      responseType: 'json',
      observe: 'response',
    });
  }
}
