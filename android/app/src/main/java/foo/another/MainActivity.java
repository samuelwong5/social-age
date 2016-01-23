package foo.another;

import android.content.Intent;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v7.app.ActionBarActivity;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;

import com.facebook.CallbackManager;
import com.facebook.FacebookCallback;
import com.facebook.FacebookException;
import com.facebook.FacebookSdk;
import com.facebook.login.LoginResult;
import com.facebook.login.widget.LoginButton;

import com.loopj.android.http.*;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.DefaultHttpClient;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.UnsupportedEncodingException;

import cz.msebera.android.httpclient.Header;


public class MainActivity extends ActionBarActivity {
    CallbackManager callbackManager;
    @Override
    protected void onCreate(Bundle savedInstanceState) {

        FacebookSdk.sdkInitialize(this);
        //If authorization is done - switch to the other activity (AccountDetails)
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        callbackManager = CallbackManager.Factory.create();
        final LoginButton loginButton = (LoginButton) findViewById(R.id.login_button);
        loginButton.registerCallback(callbackManager, new FacebookCallback<LoginResult>() {
            @Override
            public void onSuccess(LoginResult loginResult) {
                System.out.println(loginResult.getAccessToken().getToken());
                System.out.println("Created PostTask");
                //changeview(loginResult.getAccessToken().getToken());
                RequestParams params = new RequestParams("access_token", loginResult.getAccessToken().getToken());
                AsyncHttpClient client = new AsyncHttpClient();
                client.addHeader("access_token", loginResult.getAccessToken().getToken());
                client.post("http://murmuring-gorge-9791.herokuapp.com/fb_api/", params, new AsyncHttpResponseHandler() {
                    @Override
                    public void onSuccess(int statusCode, Header[] headers, byte[] responseBody) {
                        System.out.println("Success");
                        try {
                            JSONObject resultData = new JSONObject(new String(responseBody));
                            changeview(resultData);
                            System.out.println(new String(responseBody, "UTF-8"));
                        } catch (UnsupportedEncodingException e) {
                            e.printStackTrace();
                        } catch (JSONException e) {
                            e.printStackTrace();
                        }
                        System.out.println(responseBody);
                        System.out.println(headers);
                    }

                    @Override
                    public void onFailure(int statusCode, Header[] headers, byte[] responseBody, Throwable error) {
                        System.out.println("Failed");
                        System.out.println(statusCode);
                        System.out.println(headers);
                        System.out.println(error);
                        System.out.println(responseBody);
                    }
                });
                //new PostTask().doInBackground();
                System.out.println("After doInBackground()");
            }

            @Override
            public void onCancel() {
                System.out.println("Cancelled");
            }

            @Override
            public void onError(FacebookException error) {

            }
        });
        loginButton.setReadPermissions("user_likes");



//        LinearLayout layout = (LinearLayout) findViewById(R.id.linearLayout_facebookButton);
//        Button butt = new LoginButton(this);
//        layout.addView(butt);

    }

    public void changeview(JSONObject data){
        Intent intent = new Intent(this, AccountDetails.class);
        intent.putExtra("json", data.toString());
        startActivity(intent);
    }

    public void loginFacebook(View view){
        String sampleName = "Artem Kalikin";
        String sampleImage = "http://thesocialmediamonthly.com/wp-content/uploads/2015/08/photo.png";
        String sampleDescr = "This is demo. This is demo. This is demo. This is demo.This is demo. This is demo. This is demo.";
        Intent intent = new Intent(this, AccountDetails.class);
        intent.putExtra("name", sampleName);
        intent.putExtra("image", sampleImage);
        intent.putExtra("descr", sampleDescr);
        startActivity(intent);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        callbackManager.onActivityResult(requestCode, resultCode, data);
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }




}

