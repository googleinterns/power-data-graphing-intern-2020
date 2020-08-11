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
import { environment } from '../../environments/environment';
import { HttpClient, HttpParams } from '@angular/common/http';

export enum STRATEGY {
  AVG = 'avg',
  LTTB = 'lttb',
  MAX = 'max',
  MIN = 'min',
}

export interface RecordsResponse {
  data: [number, number][];
  name: string;
}
@Injectable({
  providedIn: 'root',
})
export class HttpService {

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
    timespan: number[]
  ) {
    return this.http.get(environment.apiUrl + path, {
      params: new HttpParams()
        .set('name', filename)
        .set('strategy', strategy)
        .set('start', timespan ? '' + Math.floor(timespan[0]) : null)
        .set('end', timespan ? '' + Math.floor(timespan[1]) : null),
      withCredentials: true,
    });
  }
  /**
   * Requests the server to do first-level downsampling.
   * @param path The http endpoint.
   * @param filename The file name for the experiment.
   * @param rate The frequency for downsampling.
   */
  preprocess(path: string, filename: string, rate: number) {
    return this.http.get(environment.apiUrl + path, {
      params: new HttpParams()
        .set('name', filename)
        .set('rate', rate.toString()),
      withCredentials: true,
    });
  }
}
