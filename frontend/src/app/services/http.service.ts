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

import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { STRATEGY } from '../chart/record';

export interface RecordsResponse {
  precision: number;
  data: ResponseData[];
}

export interface ResponseData {
  data: [number, number][];
  name: string;
}
@Injectable({
  providedIn: 'root',
})
export class HttpService {
  private readonly url = 'http://127.0.0.1';
  private readonly port = '5000';

  loading = false;

  constructor(private readonly http: HttpClient) {}

  /**
   * Returns an observable that retrieves the data from server.
   * @param path The http endpoint.
   * @param filename The file name for the experiment.
   * @param strategy Strategy used for downsampling.
   * @param timespan A time range in which user wish to see the records.
   */
  getRecords(
    path: string,
    filename: string,
    strategy: STRATEGY,
    number: number,
    timespan: number[]
  ) {
    return this.http.get([this.url, this.port].join(':') + path, {
      params: new HttpParams()
        .set('name', filename)
        .set('strategy', strategy)
        .set('number', number.toString())
        .set('start', timespan ? '' + Math.floor(timespan[0]) : null)
        .set('end', timespan ? '' + Math.floor(timespan[1]) : null),
    });
  }
  /**
   * Requests the server to do first-level downsampling.
   * @param path The http endpoint.
   * @param filename The file name for the experiment.
   * @param rate The frequency for downsampling.
   */
  preprocess(path: string, filename: string, rate: number) {
    return this.http.get([this.url, this.port].join(':') + path, {
      params: new HttpParams()
        .set('name', filename)
        .set('rate', rate.toString()),
    });
  }
}
