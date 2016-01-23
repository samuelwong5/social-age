package foo.another;

import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.AsyncTask;
import android.support.v7.app.ActionBarActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.DefaultHttpClient;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.MalformedURLException;
import java.net.URL;

public class AccountDetails extends ActionBarActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Intent i = getIntent();
        JSONObject data = null;
        String name = null, descr = null;
        try {
            data = new JSONObject(i.getStringExtra("json"));
        } catch (JSONException e) {
            e.printStackTrace();
        }
        try {
            name = data.getJSONObject("user").getString("name");
            descr = "Your social age is " + data.getString("social_age");
        } catch (JSONException e) {
            e.printStackTrace();
        }
        //String url = i.getStringExtra("image");
        //textView_user
        setContentView(R.layout.activity_account_details);

        ((TextView) findViewById(R.id.textView_userName)).setText(name);
        ((TextView) findViewById(R.id.textView_userDescription)).setText(descr);
        //((ImageView) findViewById(R.id.imageView_profilePicture)).setImageBitmap(new Bitmap();
    }

    public void toLikedPages(View view){

    }

}