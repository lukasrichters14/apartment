import { Injectable } from '@angular/core';
import {HttpClient, HttpErrorResponse} from "@angular/common/http";
import { Observable, throwError } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  API_URL = 'http://127.0.0.1:5000/';

  constructor(private http: HttpClient) { }

  /**
   * Submits the necessary data to the API to log a user in.
   * @param name: the user's name.
   * @param email: the user's email.
   * @param loginCode: the code given to the user to authenticate login.
   * @return : the response from the API.
   */
  login(name: string="", email: string="", loginCode: string="") {
    // Format API url based on the given parameters.
    let url = ''
    if (name && email){
      url = `${this.API_URL}login?name=${name}&email=${email}`;
    }
    else if(loginCode){
      url = `${this.API_URL}login?code=${loginCode}`;
    }
    // Login guest.
    else if(name){
      url = `${this.API_URL}login-guest?name=${name}`;
    }

    return this.http.get(url)
      .pipe(
        //retry(1), // retry a failed request up to 1 time
        catchError(ApiService.handleError) // then handle the error
      );
  }

  /**
   * Submits the necessary data to the API to register a new user.
   * @param registrationCode: the code to gain access to the API.
   * @param name: the user's name.
   * @param email: the user's email address.
   */
  register(registrationCode: string, name: string, email:string) {
    let url = `${this.API_URL}register?code=${registrationCode}&name=${name}&email=${email}`
    return this.http.get(url)
      .pipe(
        catchError(ApiService.handleError)
      )
  }

  /**
   * Handles errors that occur while attempting to access the API.
   * https://angular.io/guide/http
   * @param error: the error that occurs.
   */
  private static handleError(error: HttpErrorResponse){
    if (error.error instanceof ErrorEvent) {
      // A client-side or network error occurred.
      return throwError('There was a network error. Check your internet connection and try ' +
        'again.');
    } else {
      // The backend returned an unsuccessful response code.
      return throwError('There was an error connecting to the API.');
    }
  }
}
