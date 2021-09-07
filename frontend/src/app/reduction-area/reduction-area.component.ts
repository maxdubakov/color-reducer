import {Component, ElementRef, OnDestroy, OnInit, ViewChild} from '@angular/core';
import {ColorEvent} from "ngx-color";
import {HttpClient, HttpHeaders, HttpParams} from "@angular/common/http";
import {DomSanitizer} from "@angular/platform-browser";
import {GetCookieService} from "../get-cookie.service";

@Component({
  selector: 'app-reduction-area',
  templateUrl: './reduction-area.component.html',
  styleUrls: ['./reduction-area.component.css']
})
export class ReductionAreaComponent implements OnInit, OnDestroy {

  @ViewChild("fileDropRef", {static: false}) fileDropEl: ElementRef | undefined;
  @ViewChild('chromeComponent') chromeComponent: any;
  @ViewChild('colorInp') colorInp: ElementRef | undefined;
  @ViewChild('rubiksCube') rubiksCubeElem: ElementRef | undefined;

  server = 'http://colorreducer-env.eba-yhzwbhbv.us-east-2.elasticbeanstalk.com';

  static MAXIMUM_AREA = 100;

  currentColor: string = '#ffffff';
  handMode: boolean | undefined;
  contour: boolean | undefined;
  smoothing: boolean | undefined;
  maximumArea: number | undefined;
  pixelArt: boolean | undefined;
  amountOfColors: number | undefined;
  size: number | undefined;
  uploaded: boolean | undefined;
  converting: boolean | undefined;
  url: any;
  convertedUrl: any;
  downloadUrl: any;

  selectedColors: string[] = [];
  file: any;
  file_uploading_sub: any;

  csrf_token: string | undefined | null;
  hash_name: string | undefined;


  constructor(private http: HttpClient,
              private dom: DomSanitizer,
              private getCookie: GetCookieService) {
  }

  setDefault() {
    this.currentColor = '#fff';
    this.handMode = false;
    this.contour = false;
    this.smoothing = false;
    this.maximumArea = 0;
    this.pixelArt = false;
    this.amountOfColors = 32;
    this.size = 5;
    this.uploaded = false;
    this.converting = false;
    this.url = undefined;
    this.convertedUrl = undefined;
    this.downloadUrl = undefined;
    this.selectedColors = [];
    this.file = undefined;
    this.file_uploading_sub = undefined;
    this.hash_name = undefined;

    this.http
      .get(`${this.server}/image/csrf`)
      .subscribe(res => {
        this.csrf_token = this.getCookie.getCookie('csrftoken');
      });
  }

  ngOnInit(): void {
    this.setDefault();
  }

  ngOnDestroy() {
    this.file_uploading_sub.unsubscribe();
  }

  changeComplete($event: ColorEvent) {
    this.currentColor = $event.color.hex;
  }

  onSaveColor() {
    if (this.selectedColors.length < 16) {
      this.selectedColors.push(this.currentColor);
    }
  }

  onDeleteColor(color: any) {
    const index = this.selectedColors.indexOf(color);
    if (index > -1) {
      this.selectedColors.splice(index, 1);
    }
  }

  onFileDropped($event: any) {
    this.file = $event[0];
    this.showFile();

  }

  fileBrowseHandler($event: any) {
    this.file = $event.target.files[0];
    this.showFile();
  }

  onConvert() {
    this.converting = true;
    let params = new HttpParams();
    // @ts-ignore
    params = params.append('n', this.amountOfColors.toString());
    // @ts-ignore
    params = params.append('contour', this.contour.toString());
    // @ts-ignore
    params = params.append('rubik', this.pixelArt.toString());
    // @ts-ignore
    params = params.append('size', this.size.toString());
    // @ts-ignore
    params = params.append('smoothing', this.maximumArea.toString());
    // @ts-ignore
    params = params.append('image', this.hash_name.toString());
    if (this.handMode) {
      for (let color of this.selectedColors) {
        params = params.append('centers', color);
      }
    }
    this.http.get(`${this.server}/image/reduce`,
      {
        responseType: 'blob',
        withCredentials: false,
        params: params
      })
      .subscribe(res => {
        this.downloadUrl = window.URL.createObjectURL(res);
        this.convertedUrl = this.dom.bypassSecurityTrustUrl(this.downloadUrl);
        this.converting = false;
      });
  }

  onDownload() {
    let a = document.createElement("a");
    a.href = this.downloadUrl;
    a.download = "converted.png";
    a.click();
  }

  onDeletePicture() {
    this.setDefault();
  }

  uploadFile() {
    if (this.file) {
      const formData = new FormData();
      formData.append('image', this.file);
      // let headers = new HttpHeaders();
      // @ts-ignore
      // headers = headers.append('X-CSRFToken', this.csrf_token);
      const upload = this.http.post<{hash_name: string}>(`${this.server}/image/upload`, formData
        // {
        //   headers: headers
        // }
        );
      this.file_uploading_sub = upload.subscribe(res => {
        this.uploaded = true;
        this.hash_name = res.hash_name;
      });
    }
  }

  showFile() {
    const mimeType = this.file.type;
    if (mimeType.match(/image\/*/) == null) {
      return;
    }

    const reader = new FileReader();
    reader.readAsDataURL(this.file);
    reader.onload = (_event) => {
      this.url = reader.result;
      this.uploadFile();
    }
  }

  checkMaximumArea() {
    if (this.maximumArea !== undefined && this.maximumArea > ReductionAreaComponent.MAXIMUM_AREA) {
      this.maximumArea = ReductionAreaComponent.MAXIMUM_AREA;
    }
  }
}
