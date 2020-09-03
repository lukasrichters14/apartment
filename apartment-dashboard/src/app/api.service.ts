import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from "@angular/common/http";
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { SpotifyResponse } from "./spotifyResponse";

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
    let content;
    if (name && email){
      url = `${this.API_URL}login`;
      content = {name: name, email: email};
    }
    // Use login code.
    else if(loginCode){
      url = `${this.API_URL}login`;
      content = {code: loginCode};
    }
    // Login guest.
    else if(name){
      url = `${this.API_URL}login-guest`;
      content = {name: name};
    }

    return this.http.post(url, content)
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
    let url = `${this.API_URL}register`;
    let content = {code: registrationCode, name: name, email: email};
    return this.http.post(url, content)
      .pipe(
        catchError(ApiService.handleError)
      )
  }

  /**
   * Perform a GET request to the API to get the results of the search.
   * @param query: the search query.
   */
  spotifySearch(query: string): Observable<SpotifyResponse[]> {
    let url = `${this.API_URL}spotify/search?query=${query}`;
    return this.http.get<SpotifyResponse[]>(url)
      .pipe(
        catchError(ApiService.handleError)
      )
  }

  /**
   * Begin playback on a connected device.
   * @param uri: the Spotify URI of the song/playlist to play.
   * @param playlist: True if the given URI is a playlist, false otherwise.
   */
  spotifyStartPlayback(uri: string, playlist: boolean){
    let url = `${this.API_URL}spotify/play`
    let content = { 'uri': uri, 'playlist': playlist}
    return this.http.post(url, content)
      .pipe(
        catchError(ApiService.handleError)
      )
  }

  /**
   * Pause or resume the playback.
   * @param resume: True if the player should resume, false if the player should pause.
   */
  spotifyUpdatePlaybackState(resume: boolean) {
    let url = ''
    if (resume){
      url = `${this.API_URL}spotify/play`;
    }
    else {
      url = `${this.API_URL}spotify/pause`;
    }
    return this.http.put(url, '')
      .pipe(
        catchError(ApiService.handleError)
      )
  }

  /**
   * Get the metadata for the song that is currently playing.
   */
  spotifyGetCurrentlyPlaying(): Observable<SpotifyResponse>{
    let url = `${this.API_URL}spotify/currently-playing`
    return this.http.get<SpotifyResponse>(url)
      .pipe(
        catchError(ApiService.handleError)
      )
  }

  /**
   * Change the state of the shuffle parameter on spotify.
   * @param state: true if the shuffle should be enabled, false otherwise.
   */
  spotifyShuffle(state: boolean) {
    let url = `${this.API_URL}spotify/shuffle`
    let content = {'state': state}
    return this.http.put(url, content)
      .pipe(
        catchError(ApiService.handleError)
      )
  }

  /**
   * Add a song to the spotify queue.
   * @param uri: the Spotify URI of the song to play.
   */
  spotifyAdd(uri: string) {
    let url = `${this.API_URL}spotify/add-to-queue`
    let content = {'uri': uri}
    return this.http.post(url, content)
      .pipe(
        catchError(ApiService.handleError)
      )
  }

  spotifyGetPlaylists() {
    let url = `${this.API_URL}spotify/playlists`
    return this.http.get<SpotifyResponse[]>(url)
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
