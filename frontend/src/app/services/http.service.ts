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
  private readonly url = 'http://127.0.0.1';
  private readonly port = '5000';

  loading = false;

  constructor(private readonly http: HttpClient) {}

  /**
   *
   * @param path The http endpoint.
   * @param strategy Strategy used for downsampling.
   * @param timespan A time range in which user wish to see the records.
   */
  getRecords(path: string, strategy: STRATEGY, timespan: Date[]) {
    return this.http.get([this.url, this.port].join(':') + path, {
      params: new HttpParams()
        .set('strategy', strategy)
        .set('start', timespan ? String(timespan[0].getTime() * 1000) : null)
        .set('end', timespan ? String(timespan[1].getTime() * 1000) : null),
    });
  }
}